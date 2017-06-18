/******************************************************************************
 * pyvix - Implementation of VM Class
 * Copyright 2006 David S. Rushby
 * Available under the MIT license (see docs/license.txt for details).
 ****************************************************************************
 * 
 * Updated 4/22/2008 Adam Pridgen Adam.Pridgen@[foundstone.com || gmail.com]
 * 
 * Testing was not fully performed.  In most cases, functional testing was
 * applied.  
 * 
 * Added support for a API:
 * 
 * VixVM_AddSharedFolder
 * VixVM_CreateDirectoryInGuest
 * VixVM_CreateTempFileInGuest
 * VixVM_DeleteDirectoryInGuest
 * VixVM_DeleteFileInGuest
 * VixVM_DirectoryExistsInGuest
 * VixVM_EnableSharedFolders
 * VixVM_FileExistsInGuest
 * VixVM_GetCurrentSnapshot
 * VixVM_GetNamedSnapshot
 * VixVM_GetNumSharedFolders
 * VixVM_GetSharedFolderState
 * VixVM_KillProcessInGuest
 * VixVM_ListDirectoryInGuest
 * VixVM_ListProcessesInGuest
 * VixVM_LoginInGuest
 * VixVM_LogoutFromGuest
 * VixVM_OpenUrlInGuest
 * VixVM_PowerOn - Updated to allow for options
 * VixVM_RemoveSharedFolder
 * VixVM_RemoveSnapshot - Updated to allow for options
 * VixVM_RenameFileInGuest
 * VixVM_RevertToSnapshot - Updated to allow for options
 * VixVM_RunProgramInGuest
 * VixVM_RunScriptInGuest
 * VixVM_SetSharedFolderState
 */

/* VMTracker method declarations: */
static status VMTracker_add(VMTracker **list_slot, VM *cont);
static status VMTracker_remove(VMTracker **list_slot, VM *cont, bool);

#define VM_REQUIRE_OPEN(vm) \
	SHW_REQUIRE_OPEN((StatefulHandleWrapper *) (vm))
#define VM_isOpen StatefulHandleWrapper_isOpen
#define VM_changeState(vm, newState) \
	StatefulHandleWrapper_changeState((StatefulHandleWrapper *) (vm), newState)


static status initSupport_VM(void) {
	/* VMType is a new-style class, so PyType_Ready must be called before its
	 * getters and setters will function. */
	if (PyType_Ready(&VMType) < 0) { goto fail; }

	return SUCCEEDED;
	fail:
	/* This function is indirectly called by the module loader, which makes no
	 * provision for error recovery. */
	return FAILED;
} /* initSupport_VM */

static PyObject *pyf_VM_new(
		PyTypeObject *subtype, PyObject *args, PyObject *kwargs
)
{
	VM *self = (VM *) StatefulHandleWrapper_new(subtype);
	if (self == NULL) { goto fail; }

	/* Initialize VM-specific fields: */
	self->host = NULL;

	return (PyObject *) self;
	fail:
	assert (PyErr_Occurred());
	assert (self == NULL);
	return NULL;
} /* pyf_VM_new */

static status VM_init(VM *self, PyObject *args) {
	status res = FAILED;
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;

	Host *host;
	char *vmxPath;

	if (!PyArg_ParseTuple(args, "O!s", &HostType, &host, &vmxPath)) { goto fail; }

	assert (self->host == NULL);
	Py_INCREF(host);
	self->host = host;

	assert (self->handle == VIX_INVALID_HANDLE);
	LEAVE_PYTHON
	jobH = VixVM_Open(host->handle, vmxPath, NULL, NULL);
	err = VixJob_Wait(jobH, VIX_PROPERTY_JOB_RESULT_HANDLE, &self->handle,
			VIX_PROPERTY_NONE
	);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	assert (self->state == STATE_CREATED);
	if (VM_changeState(self, STATE_OPEN) != SUCCEEDED) { goto fail; }

	/* Enter self in the host's open VM tracker: */
	if (VMTracker_add(&host->openVMs, self) != SUCCEEDED) { goto fail; }

	res = SUCCEEDED;
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (res == FAILED);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return res;
} /* VM_init */

#define VM_clearHostReferences(vm) Py_CLEAR((vm)->host)

#define VM_hasBeenUntracked(vm) ((vm)->host == NULL)

static status VM_close_withoutUnlink(VM *self, bool allowedToRaise) {
	if (self->openSnapshots != NULL) {
		if (SnapshotTracker_release(&self->openSnapshots) == SUCCEEDED) {
			assert (self->openSnapshots == NULL);
		} else {
			if (allowedToRaise) { goto fail; } else { SUPPRESS_EXCEPTION; }
		}
	}

	if (self->state == STATE_OPEN && self->handle != VIX_INVALID_HANDLE) {
		LEAVE_PYTHON
		Vix_ReleaseHandle(self->handle);
		self->handle = VIX_INVALID_HANDLE;
		ENTER_PYTHON
	}

	assert (self->handle == VIX_INVALID_HANDLE);
	if (VM_changeState(self, STATE_CLOSED) != SUCCEEDED) { goto fail; }

	return SUCCEEDED;
	fail:
	assert (PyErr_Occurred());
	return FAILED;
} /* VM_close_withoutUnlink */

static status VM_close_withUnlink(VM *self, bool allowedToRaise) {
	/* Since the caller is asking us to unlink, self should still have a host,
	 * and self should be present in the host's open VM tracker. */
	assert (self->host != NULL);
	assert (self->host->openVMs != NULL);

	if (VM_close_withoutUnlink(self, allowedToRaise) == SUCCEEDED) {
		assert (self->state == STATE_CLOSED);
	} else {
		if (allowedToRaise) { goto fail; } else { SUPPRESS_EXCEPTION; }
	}

	/* Remove self from the host's open VM tracker: */
	if (VMTracker_remove(&self->host->openVMs, self, true) != SUCCEEDED) {
		if (allowedToRaise) { goto fail; } else { SUPPRESS_EXCEPTION; }
	}

	VM_clearHostReferences(self);

	assert (VM_hasBeenUntracked(self));
	return SUCCEEDED;
	fail:
	assert (PyErr_Occurred());
	return FAILED;
} /* VM_close_withUnlink */

static PyObject *pyf_VM_close(VM *self, PyObject *args) {
	VM_REQUIRE_OPEN(self);
	if (VM_close_withUnlink(self, true) != SUCCEEDED) { goto fail; }
	Py_RETURN_NONE;
	fail:
	assert (PyErr_Occurred());
	return NULL;
} /* pyf_VM_close */

static PyObject *pyf_VM_closed_get(VM *self, void *closure) {
	return PyBool_FromLong(!VM_isOpen(self));
} /* pyf_VM_closed_get */

static status VM_untrack(VM *self, bool allowedToRaise) {
	if (VM_close_withoutUnlink(self, allowedToRaise) != SUCCEEDED) {
		return FAILED;
	}
	assert (!VM_isOpen(self));

	VM_clearHostReferences(self);
	assert (VM_hasBeenUntracked(self));

	return SUCCEEDED;
} /* VM_untrack */

static status VM_delete(VM *self, bool allowedToRaise) {
	if (self->state == STATE_OPEN) {
		if (VM_close_withUnlink(self, allowedToRaise) == SUCCEEDED) {
			assert (VM_hasBeenUntracked(self));
		} else {
			if (allowedToRaise) { goto fail; } else { SUPPRESS_EXCEPTION; }
		}
	}

	return SUCCEEDED;
	fail:
	assert (PyErr_Occurred());
	return FAILED;
} /* VM_delete */

static void pyf_VM___del__(VM *self) {
	VM_delete(self, false);

	/* Release the VM struct itself: */
	self->ob_type->tp_free((PyObject *) self);
} /* pyf_VM___del__ */

static PyObject *pyf_VM_powerOnOrOff(VM *self,
		PyObject *args, bool shouldPowerOn) {
	
	
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;
	int options = VIX_VMPOWEROP_NORMAL;
	
	VM_REQUIRE_OPEN(self);
	
	if (!PyArg_ParseTuple(args, "|i",&options)) { goto fail; }
	
	if (options != VIX_VMPOWEROP_NORMAL && options != VIX_VMPOWEROP_LAUNCH_GUI){
		options = VIX_VMPOWEROP_NORMAL; 
	}
	LEAVE_PYTHON
	
	
	if (shouldPowerOn) {
		jobH = VixVM_PowerOn(self->handle, options,
				VIX_INVALID_HANDLE, NULL, NULL
		);
	} else {
		jobH = VixVM_PowerOff(self->handle, 0, NULL, NULL);
	}
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_powerOn */

static PyObject *pyf_VM_powerOn(VM *self,
		PyObject *args) {
	
	return pyf_VM_powerOnOrOff(self, args, true);
} /* pyf_VM_powerOn */

static PyObject *pyf_VM_powerOff(VM *self,
		PyObject *args) {
	return pyf_VM_powerOnOrOff(self, args, false);
} /* pyf_VM_powerOn */

static PyObject *pyf_VM_reset(VM *self) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_Reset(self->handle,
			/* powerOnOptions:  Must be VIX_VMPOWEROP_NORMAL in current release: */
			VIX_VMPOWEROP_NORMAL,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_reset */

static PyObject *pyf_VM_suspend(VM *self) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_Suspend(self->handle,
			/* powerOffOptions:  Must be VIX_VMPOWEROP_NORMAL in current release: */
			VIX_VMPOWEROP_NORMAL,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_suspend */

static PyObject *pyf_VM_upgradeVirtualHardware(VM *self) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_UpgradeVirtualHardware(self->handle,
			0, /* options:  Must be 0 in current release. */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_upgradeVirtualHardware */

static PyObject *pyf_VM_waitForToolsInGuest(VM *self, PyObject *args) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;
	VixToolsState toolsState = VIX_TOOLSSTATE_UNKNOWN;

	int timeoutSecs = NO_TIMEOUT;

	VM_REQUIRE_OPEN(self);
	if (!PyArg_ParseTuple(args, "|i", &timeoutSecs)) { goto fail; }

	LEAVE_PYTHON
	/* XXX: As of VMWare Server 1.0RC1, the timeout either doesn't work, or
	 * requires the use of the async callback instead of VixJob_Wait.  At any
	 * rate, the timeout doesn't work as expected at present. */
	jobH = VixVM_WaitForToolsInGuest(self->handle, timeoutSecs, NULL, NULL);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	LEAVE_PYTHON
	err = Vix_GetProperties(self->handle, VIX_PROPERTY_VM_TOOLS_STATE,
			&toolsState, VIX_PROPERTY_NONE
	);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	/* If the VM's "tools state" is still undefined even after the VixJob_Wait
	 * call returned, then we timed out. */
	pyRes = PyBool_FromLong(toolsState != VIX_TOOLSSTATE_UNKNOWN);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_waitForToolsInGuest */

static PyObject *pyf_VM_installTools(VM *self) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_InstallTools(self->handle,
			0, /* options:  Must be 0 in current release. */
			NULL, /* commandLineArgs:  Must be NULL in current release. */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_installTools */

static PyObject *pyf_VM_delete(VM *self) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_Delete(self->handle,
			0, /* deleteOptions:  Must be 0 in current release. */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_delete */

static PyObject *pyf_VM_createSnapshot(VM *self,
		PyObject *args, PyObject *kwargs
)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pySnap = NULL;
	VixHandle snapH;

	static char* kwarg_list[] = {"name", "description", "options", NULL};
	char *name = NULL;
	char *description = NULL;
	int options = 0;

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ssi", kwarg_list,
			&name, &description, &options
	))
	{ goto fail; }
	
	LEAVE_PYTHON
	jobH = VixVM_CreateSnapshot(self->handle,
			name, description, options,
			/* propertyListHandle:  Must be VIX_INVALID_HANDLE in current release: */
			VIX_INVALID_HANDLE,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH,
			VIX_PROPERTY_JOB_RESULT_HANDLE, &snapH,
			VIX_PROPERTY_NONE
	);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	assert (snapH != VIX_INVALID_HANDLE);
	pySnap = PyObject_CallFunction((PyObject *) &SnapshotType,
			"O" VixHandle_FUNCTION_CALL_CODE, self, snapH
	);
	/* If the creation of pySnap succeeded, the Snapshot instance now owns snapH;
	 * if the creation failed, we need to release snapH: */
	if (pySnap == NULL) {
		Vix_ReleaseHandle(snapH);
		goto fail;
	}

	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	Py_XDECREF(pySnap);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pySnap;
} /* pyf_VM_createSnapshot */

static PyObject *pyf_VM_getNamedSnapshot(VM *self, PyObject *args)
{
	VixError err;
	PyObject *pySnap = NULL;
	VixHandle snapH;

	char *snapshotname = NULL;

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &snapshotname)) { goto fail;}
	
	printf("snapshotname: %s",snapshotname);
	LEAVE_PYTHON
	err = VixVM_GetNamedSnapshot(self->handle,
			snapshotname,
			&snapH);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);
	if (snapH != VIX_INVALID_HANDLE){goto fail;}
	
	pySnap = PyObject_CallFunction((PyObject *) &SnapshotType,
			"O" VixHandle_FUNCTION_CALL_CODE, self, snapH
	);
	/* If the creation of pySnap succeeded, the Snapshot instance now owns snapH;
	 * if the creation failed, we need to release snapH: */
	if (pySnap == NULL) {
		Vix_ReleaseHandle(snapH);
		goto fail;
	}

	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	if (pySnap != NULL) {Py_XDECREF(pySnap);}
	pySnap = Py_None;
	Py_INCREF(Py_None);
	/* Fall through to cleanup: */
	cleanup:
	return pySnap;
} /* pyf_VM_getNamedSnapshot */

static PyObject *pyf_VM_getCurrentSnapshot(VM *self, PyObject *args)
{
	VixError err;
	PyObject *pySnap = NULL;
	
	VixHandle snapH;  

	VM_REQUIRE_OPEN(self);
	LEAVE_PYTHON
	err = VixVM_GetCurrentSnapshot(self->handle, &snapH);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	if (snapH != VIX_INVALID_HANDLE){goto fail; }
	
	pySnap = PyObject_CallFunction((PyObject *) &SnapshotType,
			"O" VixHandle_FUNCTION_CALL_CODE, self, snapH);
	/* If the creation of pySnap succeeded, the Snapshot instance now owns snapH;
	 * if the creation failed, we need to release snapH: */
	if (pySnap == NULL) {
		Vix_ReleaseHandle(snapH);
		goto fail;
	}

	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	if (pySnap != NULL) {Py_XDECREF(pySnap);}
	Py_XDECREF(pySnap);
	pySnap = Py_None;
	Py_INCREF(Py_None);
		
	/* Fall through to cleanup: */
	cleanup:
	return pySnap;
} /* pyf_VM_getCurrentSnapshot */

static PyObject *pyf_VM_removeSnapshot(VM *self, PyObject *args){
	PyObject *pyRes = NULL;
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	
	Snapshot *pySnap;
	int options = 0;
	VM_REQUIRE_OPEN(self);
	
	
	if (!PyArg_ParseTuple(args, "O!|i", &SnapshotType, &pySnap, &options))
		{ goto fail; }
	
	
	if (options != 0 && options != VIX_SNAPSHOT_REMOVE_CHILDREN) {options = 0;}
	LEAVE_PYTHON
	jobH = VixVM_RemoveSnapshot(self->handle,
			pySnap->handle,
			options, /* options:  Must be 0 in current release. */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_removeSnapshot */

static PyObject *pyf_VM_revertToSnapshot(VM *self, PyObject *args, PyObject *kwargs) {
	PyObject *pyRes = NULL;
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;

	Snapshot *pySnap;
	int options = VIX_VMPOWEROP_NORMAL;
	VM_REQUIRE_OPEN(self);

	
	
	if (!PyArg_ParseTuple(args, "O!|i",&SnapshotType, 
						&pySnap, &options))
		{ goto fail; }
	
	if (options & VIX_VMPOWEROP_SUPPRESS_SNAPSHOT_POWERON){
		options = VIX_VMPOWEROP_SUPPRESS_SNAPSHOT_POWERON;
	}
	LEAVE_PYTHON
	jobH = VixVM_RevertToSnapshot(self->handle,
			pySnap->handle,
			options, /* options:  Must be 0 in current release. */
			/* propertyListHandle:  Must be VIX_INVALID_HANDLE in current release: */
			VIX_INVALID_HANDLE,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_revertToSnapshot */

static PyObject *pyf_VM_loginInGuest(VM *self,
		PyObject *args, PyObject *kwargs
)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	static char* kwarg_list[] = {"username", "password", "options", NULL};
	char *username = NULL;
	char *password = NULL;
	int options = 0;

	VM_REQUIRE_OPEN(self);
	/* fixed to allow for blank passwords, cause you know users use them :) atp*/
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s|si", kwarg_list,
			&username, &password, &options
	))
	{ 
		goto fail; 
	}
	if (password == NULL) {password = "";}
			
			
	LEAVE_PYTHON
	jobH = VixVM_LoginInGuest(self->handle,
			username, password, options,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_loginInGuest */
static PyObject *pyf_VM_logoutFromGuest(VM *self,
		PyObject *args, PyObject *kwargs
)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	jobH = VixVM_LogoutFromGuest(self->handle,
            NULL, // callbackProc
            NULL); // clientData

	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_logoutFromGuest */

static PyObject *pyf_VM_copyFile(VM *self, PyObject *args,
		bool fromHostToGuest
)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *src;
	char *dest;

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "ss", &src, &dest)) { goto fail; }

	LEAVE_PYTHON
	if (fromHostToGuest) {
		jobH = VixVM_CopyFileFromHostToGuest(self->handle,
				src, dest,
				0, /* options:  Must be 0 in current release. */
				/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
				VIX_INVALID_HANDLE,
				NULL, /* callbackProc */
				NULL  /* clientData */
		);
	} else {
		jobH = VixVM_CopyFileFromGuestToHost(self->handle,
				src, dest,
				0, /* options:  Must be 0 in current release. */
				/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
				VIX_INVALID_HANDLE,
				NULL, /* callbackProc */
				NULL  /* clientData */
		);
	}
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_copyFile */

static PyObject *pyf_VM_copyFileFromHostToGuest(VM *self, PyObject *args) {
	return pyf_VM_copyFile(self, args, true);
} /* pyf_VM_copyFileFromHostToGuest */

static PyObject *pyf_VM_copyFileFromGuestToHost(VM *self, PyObject *args) {
	return pyf_VM_copyFile(self, args, false);
} /* pyf_VM_copyFileFromGuestToHost */

static PyObject *pyf_VM_runProgramInGuest(VM *self, PyObject *args) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	VixCallbackAccumulator acc;	
	PyObject *pyRes = NULL;

	
	char *progPath;
	char *commandLine;
	int options = 0;
	
	if (VixCallbackAccumulator_TupleInit(&acc, 3) != SUCCEEDED) { goto fail; }

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "ss|i", &progPath, &commandLine, &options)) { goto fail; }
	
	options &= VIX_RUNPROGRAM_ACTIVATE_WINDOW | VIX_RUNPROGRAM_RETURN_IMMEDIATELY;
	
	LEAVE_PYTHON
	jobH = VixVM_RunProgramInGuest(self->handle,
			progPath, commandLine,
			options, /* options */
			/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
			VIX_INVALID_HANDLE,
			VixCallback_accumulateProcessStats, /* callbackProc */
			&acc  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	
	CHECK_VIX_ERROR(err);
	pyRes = acc.target;
	acc.target = NULL;
	goto cleanup;
	fail:
	  assert (PyErr_Occurred());
	  assert (pyRes == NULL);
	  VixCallbackAccumulator_clear(&acc);
	    /* Fall through to cleanup: */
	cleanup:
	  if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	  return pyRes;
} /* pyf_VM_runProgramInGuest */

static PyObject *pyf_VM_openUrlInGuest(VM *self, PyObject *args) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;
	char *url;
	
	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &url)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_OpenUrlInGuest(self->handle,
			                      url,
			                      0, // options,
			                      VIX_INVALID_HANDLE, // propertyListHandle,
			                      NULL, // callbackProc,
			                      NULL); // clientData
	
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_openUrlInGuest */

static PyObject *pyf_VM_runScriptInGuest(VM *self, PyObject *args) {
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;
	VixCallbackAccumulator acc;
	char *scripttext, *interpreter;
	int options = 0;
	VM_REQUIRE_OPEN(self);
	
	if (VixCallbackAccumulator_TupleInit(&acc, 3) != SUCCEEDED) { goto fail; }
	if (!PyArg_ParseTuple(args, "ss|i", &interpreter, &scripttext, &options)) { goto fail; }
	
	options &= VIX_RUNPROGRAM_ACTIVATE_WINDOW | VIX_RUNPROGRAM_RETURN_IMMEDIATELY;
	
	LEAVE_PYTHON
	jobH = VixVM_RunScriptInGuest(self->handle,
			                      interpreter,
			                      scripttext,
			                      options, // options,
			                      VIX_INVALID_HANDLE, // propertyListHandle,
			                  	  VixCallback_accumulateProcessStats, /* callbackProc */
			                  	  &acc  /* clientData */
								);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	
	CHECK_VIX_ERROR(err);
	pyRes = acc.target;
	acc.target = NULL;
	goto cleanup;
	fail:
	  assert (PyErr_Occurred());
	  assert (pyRes == NULL);
	  VixCallbackAccumulator_clear(&acc);
	    /* Fall through to cleanup: */
	cleanup:
	  if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	  return pyRes;
} /* pyf_VM_runScriptInGuest */

static PyObject *pyf_VM_host_get(VM *self, void *closure) {
	PyObject *host = (self->host != NULL ? (PyObject *) self->host : Py_None);
	Py_INCREF(host);
	return host;
} /* pyf_VM_host_get */

static PyObject *pyf_VM_nRootSnapshots_get(VM *self, void *closure) {
	VixError err = VIX_OK;
	int nRootSnapshots;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	err = VixVM_GetNumRootSnapshots(self->handle, &nRootSnapshots);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	return PyInt_FromLong(nRootSnapshots);
	fail:
	assert (PyErr_Occurred());
	return NULL;
} /* pyf_VM_nRootSnapshots_get */

static PyObject *pyf_VM_rootSnapshots_get(VM *self, void *closure) {
	VixError err = VIX_OK;
	int nRootSnapshots = -1;
	int i;
	PyObject *pySnapList = NULL;

	VM_REQUIRE_OPEN(self);

	LEAVE_PYTHON
	err = VixVM_GetNumRootSnapshots(self->handle, &nRootSnapshots);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	assert (nRootSnapshots >= 0);
	pySnapList = PyList_New(nRootSnapshots);
	if (pySnapList == NULL) { goto fail; }

	for (i = 0; i < nRootSnapshots; i++) {
		VixHandle snapH = VIX_INVALID_HANDLE;
		PyObject *pySnap = NULL;

		LEAVE_PYTHON
		err = VixVM_GetRootSnapshot(self->handle, i, &snapH);
		ENTER_PYTHON
		CHECK_VIX_ERROR(err);

		assert (snapH != VIX_INVALID_HANDLE);
		pySnap = PyObject_CallFunction((PyObject *) &SnapshotType,
				"Oi", self, snapH
		);
		/* If the creation of pySnap succeeded, the Snapshot instance now owns
		 * snapH; if the creation failed, we need to release snapH: */
		if (pySnap == NULL) {
			Vix_ReleaseHandle(snapH);
			goto fail;
		}

		/* PyList_SET_ITEM steals our reference to pySnap: */
		PyList_SET_ITEM(pySnapList, i, pySnap);
	}

	assert (pySnapList != NULL);
	assert (PyList_GET_SIZE(pySnapList) == (Py_ssize_t) nRootSnapshots);
	return pySnapList;
	fail:
	assert (PyErr_Occurred());
	Py_XDECREF(pySnapList);
	return NULL;
} /* pyf_VM_rootSnapshots_get */
static PyObject *pyf_VM_createDirectoryInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *pathname;


	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_CreateDirectoryInGuest(self->handle,
			pathname,
			/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
			VIX_INVALID_HANDLE,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_createDirectoryInGuest */


static PyObject *pyf_VM_listDirectoryInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	VixCallbackAccumulator acc;	
	PyObject *pyRes = NULL;
	char *pathname = NULL;
	
	VM_REQUIRE_OPEN(self);
	
	if (VixCallbackAccumulator_ListInit(&acc) != SUCCEEDED) { goto fail; }

	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_ListDirectoryInGuest(self->handle,
			pathname,
			0, /* options */
			VixCallback_accumulateDirectoryList, &acc);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	
	CHECK_VIX_ERROR(err);
	pyRes = acc.target;
	acc.target = NULL;
	goto cleanup;
	fail:
	  assert (PyErr_Occurred());
	  assert (pyRes == NULL);
	  VixCallbackAccumulator_clear(&acc);
	    /* Fall through to cleanup: */
	cleanup:
	  if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	  return pyRes;
} /* pyf_VM_listDirectoryInGuest */

static PyObject *pyf_VM_renameFileInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *oldname = NULL, 
		 *newname = NULL;

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "ss", &oldname, &newname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_RenameFileInGuest(self->handle,
			oldname,
			newname,
			0, /* options */
			VIX_INVALID_HANDLE, /* property Handle */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);

	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_renameFileInGuest */


static PyObject *pyf_VM_deleteDirectoryInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *pathname;


	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_DeleteDirectoryInGuest(self->handle,
			pathname,
			/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
			VIX_INVALID_HANDLE,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_deleteDirectoryInGuest */
static PyObject *pyf_VM_deleteFileInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *pathname;


	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_DeleteFileInGuest(self->handle,
			pathname,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_deleteFileInGuest */



static PyObject *pyf_VM_directoryExistsInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *res = NULL;
	long exists = 0;
	char *pathname;


	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_DirectoryExistsInGuest(self->handle,
			pathname,
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS,
			&exists,
			VIX_PROPERTY_NONE);

	ENTER_PYTHON
	CHECK_VIX_ERROR(err);
	res = PyBool_FromLong(exists);
	//assert (PyBool_CheckExact(res));

	if (res == NULL){goto fail;}
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (res == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return res;
} /* pyf_VM_deleteFileInGuest */

static PyObject *pyf_VM_getNumSharedFolders(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyResult = NULL;
	int numSharedFolders;


	VM_REQUIRE_OPEN(self);
	LEAVE_PYTHON
	jobH = VixVM_GetNumSharedFolders(self->handle, NULL, NULL);
	err = VixJob_Wait(jobH,
			VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_COUNT,
			&numSharedFolders,
			VIX_PROPERTY_NONE);

	ENTER_PYTHON

	CHECK_VIX_ERROR(err);
	pyResult = PyInt_FromLong(numSharedFolders);
	assert(PyInt_CheckExact(pyResult));

	if (pyResult == NULL) {
		goto fail;
	}

	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyResult == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyResult;
} /* pyf_VM_getNumSharedFolders */

static PyObject *pyf_VM_getSharedFolderState(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	VixCallbackAccumulator acc;
	PyObject *pyResult = NULL;
	
	unsigned int i = 0;
	
	VM_REQUIRE_OPEN(self);
		
	if (VixCallbackAccumulator_TupleInit(&acc, 3) != SUCCEEDED) { goto fail; }
	
	if (!PyArg_ParseTuple(args, "i", &i)) { goto fail; }
	VM_REQUIRE_OPEN(self);
	
	LEAVE_PYTHON
	jobH = VixVM_GetSharedFolderState(self->handle, i, VixCallback_accumulateSharedStateList, &acc);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	
	CHECK_VIX_ERROR(err);
	pyResult = acc.target;
	acc.target = NULL;
	goto cleanup;
	fail:
	  assert (PyErr_Occurred());
	  assert (pyResult == NULL);
	  VixCallbackAccumulator_clear(&acc);
	  /* Fall through to cleanup: */
	cleanup:
	  if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	  return pyResult;
} /* pyf_VM_getSharedFolderState */
static PyObject *pyf_VM_setSharedFolderState(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyResult = NULL;

	char *folderName = NULL,
	*folderHostPath = NULL;
	int folderFlags = 0;

	if (!PyArg_ParseTuple(args, "ssi", &folderName, &folderHostPath, &folderFlags)) { goto fail; }
	VM_REQUIRE_OPEN(self);
	LEAVE_PYTHON
	jobH = VixVM_SetSharedFolderState(self->handle, folderName, folderHostPath,
	                                          folderFlags,
	                                          NULL, NULL);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON

	CHECK_VIX_ERROR(err);

	pyResult = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyResult == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyResult;
} /* pyf_VM_setSharedFolderState */

static PyObject *pyf_VM_addSharedFolder(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	char *pathname;
	char *sharename;

	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "ss", &sharename, &pathname)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_AddSharedFolder(self->handle,
			sharename,
			pathname,
			VIX_SHAREDFOLDER_WRITE_ACCESS, /* options:  Must be 0 in current release. */
			/* propertyList:  Must be VIX_INVALID_HANDLE in current release: */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_addSharedFolder */

static PyObject *pyf_VM_enableorDisableSharedFolders(VM *self, PyObject *args, bool enableSF)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *pyRes = NULL;
	VM_REQUIRE_OPEN(self);
	LEAVE_PYTHON
	if (enableSF)  /* enable shared Folders */
		jobH = VixVM_EnableSharedFolders(self->handle,
				enableSF, /* bool Enabled shared Folders */
				0, /* options:  Must be 0 in current release. */
				NULL, 
				NULL
		);
	else /* disable shared folders */
		jobH = VixVM_EnableSharedFolders(self->handle,
				enableSF, /* bool Enabled shared Folders */
				0, /* options:  Must be 0 in current release. */
				NULL, 
				NULL
		);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	 
	pyRes = Py_None;
	Py_INCREF(Py_None);
	
	if (pyRes == NULL){goto fail;}
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_enableorDisableSharedFolders */
static PyObject *pyf_VM_enableSharedFolders(VM *self, PyObject *args){
	return pyf_VM_enableorDisableSharedFolders(self, args, TRUE);
} /* pyf_VM_enableSharedFolders */
static PyObject *pyf_VM_disableSharedFolders(VM *self, PyObject *args){
	return pyf_VM_enableorDisableSharedFolders(self, args, FALSE);
} /* pyf_VM_disableSharedFolders */

static PyObject *pyf_VM_createTempFileInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *res = NULL;
	char *temppath = NULL;


	VM_REQUIRE_OPEN(self);



	LEAVE_PYTHON
	jobH = VixVM_CreateTempFileInGuest(self->handle,
			0, /* options:  Must be 0 in current release. */
			VIX_INVALID_HANDLE,
			NULL, 
			NULL
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS,
			&temppath,
			VIX_PROPERTY_NONE);

	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	if (temppath == NULL){ goto fail;}
	res =  PyString_FromString(temppath); 
	assert (PyString_CheckExact(res));

	if (res == NULL){goto fail;}
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (res == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return res;
} /* pyf_VM_createTempFileInGuest */

static PyObject *pyf_VM_fileExistsInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err = VIX_OK;
	PyObject *res = NULL;
	char *pathname = NULL;
	long exists;

	VM_REQUIRE_OPEN(self);
	if (!PyArg_ParseTuple(args, "s", &pathname)) { goto fail; }


	LEAVE_PYTHON
	jobH = VixVM_FileExistsInGuest(self->handle,
			pathname, 
			NULL, 
			NULL
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_JOB_RESULT_GUEST_OBJECT_EXISTS,
			&exists,
			VIX_PROPERTY_NONE);

	ENTER_PYTHON
	CHECK_VIX_ERROR(err);
	res = PyBool_FromLong(exists);
	//assert (PyBool_CheckExact(res));

	if (res == NULL){goto fail;}
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (res == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return res;
} /* pyf_VM_fileExistsInGuest */


static PyObject *pyf_VM_listProcessesInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	VixCallbackAccumulator acc;	
	PyObject *pyRes = NULL;

	VM_REQUIRE_OPEN(self);
	if (VixCallbackAccumulator_ListInit(&acc) != SUCCEEDED) { goto fail; }
	
	LEAVE_PYTHON
	jobH = VixVM_ListProcessesInGuest(self->handle, 0, VixCallback_accumulateProcessList, &acc);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	
	CHECK_VIX_ERROR(err);
	pyRes = acc.target;
	acc.target = NULL;
	goto cleanup;
	fail:
	  assert (PyErr_Occurred());
	  assert (pyRes == NULL);
	  VixCallbackAccumulator_clear(&acc);
	    /* Fall through to cleanup: */
	cleanup:
	  if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	  return pyRes;
} /* pyf_VM_listProcessesInGuest */


static PyObject *pyf_VM_killProcessInGuest(VM *self, PyObject *args)
{
	VixHandle jobH = VIX_INVALID_HANDLE;
	VixError err;
	PyObject *pyRes = NULL;

	uint64 pid;


	VM_REQUIRE_OPEN(self);

	if (!PyArg_ParseTuple(args, "i", &pid)) { goto fail; }

	LEAVE_PYTHON
	jobH = VixVM_KillProcessInGuest(self->handle,
			pid,
			0, /* options:  Must be 0 in current release. */
			NULL, /* callbackProc */
			NULL  /* clientData */
	);
	err = VixJob_Wait(jobH, VIX_PROPERTY_NONE);
	ENTER_PYTHON
	CHECK_VIX_ERROR(err);

	pyRes = Py_None;
	Py_INCREF(Py_None);
	goto cleanup;
	fail:
	assert (PyErr_Occurred());
	assert (pyRes == NULL);
	/* Fall through to cleanup: */
	cleanup:
	if (jobH != VIX_INVALID_HANDLE) { Vix_ReleaseHandle(jobH); }
	return pyRes;
} /* pyf_VM_killProcessInGuest */
static PyMethodDef VM_methods[] = {
		{"close",
				(PyCFunction) pyf_VM_close,
				METH_NOARGS
		},
		{"powerOn",
				(PyCFunction) pyf_VM_powerOn,
				METH_NOARGS
		},
		{"powerOff",
				(PyCFunction) pyf_VM_powerOff,
				METH_NOARGS
		},
		{"reset",
				(PyCFunction) pyf_VM_reset,
				METH_NOARGS
		},
		{"suspend",
				(PyCFunction) pyf_VM_suspend,
				METH_NOARGS
		},
		{"installTools",
				(PyCFunction) pyf_VM_installTools,
				METH_NOARGS
		},
		{"waitForToolsInGuest",
				(PyCFunction) pyf_VM_waitForToolsInGuest,
				METH_VARARGS
		},
		{"upgradeVirtualHardware",
				(PyCFunction) pyf_VM_upgradeVirtualHardware,
				METH_NOARGS
		},
		{"delete",
				(PyCFunction) pyf_VM_delete,
				METH_NOARGS
		},
		{"createSnapshot",
				/* It should actually be PyCFunctionWithKeywords, but GCC grumbles
				 * about that: */
				(PyCFunction) pyf_VM_createSnapshot,
				METH_VARARGS | METH_KEYWORDS,
		},
		{"getCurrentSnapshot",
				/* It should actually be PyCFunctionWithKeywords, but GCC grumbles
				 * about that: */
				(PyCFunction) pyf_VM_getCurrentSnapshot,
				METH_VARARGS | METH_KEYWORDS,
		},
		{"getNamedSnapshot",
				/* It should actually be PyCFunctionWithKeywords, but GCC grumbles
				 * about that: */
				(PyCFunction) pyf_VM_getNamedSnapshot,
				METH_VARARGS | METH_KEYWORDS,
		},
		{"removeSnapshot",
				(PyCFunction) pyf_VM_removeSnapshot,
				METH_VARARGS
		},
		{"revertToSnapshot",
				(PyCFunction) pyf_VM_revertToSnapshot,
				METH_VARARGS
		},
		{"loginInGuest",
				/* It should actually be PyCFunctionWithKeywords, but GCC grumbles
				 * about that: */
				(PyCFunction) pyf_VM_loginInGuest,
				METH_VARARGS | METH_KEYWORDS,
		},
		{"logoutFromGuest",
				/* It should actually be PyCFunctionWithKeywords, but GCC grumbles
				 * about that: */
				(PyCFunction) pyf_VM_logoutFromGuest,
				METH_VARARGS | METH_KEYWORDS,
		},

		{"copyFileFromHostToGuest",
				(PyCFunction) pyf_VM_copyFileFromHostToGuest,
				METH_VARARGS
		},
		{"copyFileFromGuestToHost",
				(PyCFunction) pyf_VM_copyFileFromGuestToHost,
				METH_VARARGS
		},
		{"runProgramInGuest",
				(PyCFunction) pyf_VM_runProgramInGuest,
				METH_VARARGS
		},
		{"runScriptInGuest",
				(PyCFunction) pyf_VM_runScriptInGuest,
				METH_VARARGS
		},
		{"openUrlInGuest",
				(PyCFunction) pyf_VM_openUrlInGuest,
				METH_VARARGS
		},
		{"createDirectoryInGuest",
				(PyCFunction) pyf_VM_createDirectoryInGuest,
				METH_VARARGS
		},
		{"renameFileInGuest",
				(PyCFunction) pyf_VM_renameFileInGuest,
				METH_VARARGS
		},
		{"listDirectoryInGuest",
				(PyCFunction) pyf_VM_listDirectoryInGuest,
				METH_VARARGS
		},
		{"directoryExistsInGuest",
				(PyCFunction) pyf_VM_directoryExistsInGuest,
				METH_VARARGS
		},
		{"deleteDirectoryInGuest",
				(PyCFunction) pyf_VM_deleteDirectoryInGuest,
				METH_VARARGS
		},
		{"deleteFileInGuest",
				(PyCFunction) pyf_VM_deleteFileInGuest,
				METH_VARARGS
		},
		{"createTempFileInGuest",
				(PyCFunction) pyf_VM_createTempFileInGuest,
				METH_VARARGS
		},
		{"fileExistsInGuest",
				(PyCFunction) pyf_VM_fileExistsInGuest,
				METH_VARARGS
		},
		{"addSharedFolder",
				(PyCFunction) pyf_VM_addSharedFolder,
				METH_VARARGS
		},
		{"enableSharedFolders",
				(PyCFunction) pyf_VM_enableSharedFolders,
				METH_VARARGS
		},
		{"disableSharedFolders",
				(PyCFunction) pyf_VM_disableSharedFolders,
				METH_VARARGS
		},
		{"getNumSharedFolders",
				(PyCFunction) pyf_VM_getNumSharedFolders,
				METH_VARARGS
		},
		{"getSharedFolderState",
				(PyCFunction) pyf_VM_getSharedFolderState,
				METH_VARARGS
		},
		{"setSharedFolderState",
				(PyCFunction) pyf_VM_setSharedFolderState,
				METH_VARARGS
		},
		{"listProcessesInGuest",
				(PyCFunction) pyf_VM_listProcessesInGuest,
				METH_VARARGS
		},
		{"killProcessInGuest",
				(PyCFunction) pyf_VM_killProcessInGuest,
				METH_VARARGS
		},
		{NULL}  /* sentinel */
};

static PyGetSetDef VM_getters_setters[] = {
		{"closed",
				(getter) pyf_VM_closed_get,
				NULL,
				"True if the VM is *known* to be closed."
		},
		{"host",
				(getter) pyf_VM_host_get,
				NULL,
				"The Host on which this VM resides."
		},
		{"nRootSnapshots",
				(getter) pyf_VM_nRootSnapshots_get,
				NULL,
				"The number of root snapshots in this VM (the length of the list"
				" returned by the rootSnapshots property)."
		},
		{"rootSnapshots",
				(getter) pyf_VM_rootSnapshots_get,
				NULL,
				"A list of Snapshot objects that represent the root snapshots in this"
				" VM."
		},
		{NULL}  /* sentinel */
};

PyTypeObject VMType = { /* new-style class */
		PyObject_HEAD_INIT(NULL)
		0,                                  /* ob_size */
		"pyvix.vix.VM",                     /* tp_name */
		sizeof(VM),                         /* tp_basicsize */
		0,                                  /* tp_itemsize */
		(destructor) pyf_VM___del__,        /* tp_dealloc */
		0,                                  /* tp_print */
		0,                                  /* tp_getattr */
		0,                                  /* tp_setattr */
		0,                                  /* tp_compare */
		0,                                  /* tp_repr */
		0,                                  /* tp_as_number */
		0,                                  /* tp_as_sequence */
		&StatefulHandleWrapper_as_mapping,  /* tp_as_mapping */
		0,                                  /* tp_hash */
		0,                                  /* tp_call */
		0,                                  /* tp_str */
		0,                                  /* tp_getattro */
		0,                                  /* tp_setattro */
		0,                                  /* tp_as_buffer */
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
		/* tp_flags */
		0,                                  /* tp_doc */
		0,		                              /* tp_traverse */
		0,		                              /* tp_clear */
		0,		                              /* tp_richcompare */
		0,		                              /* tp_weaklistoffset */

		0,                    		          /* tp_iter */
		0,		                              /* tp_iternext */

		VM_methods,                         /* tp_methods */
		NULL,                               /* tp_members */
		VM_getters_setters,                 /* tp_getset */
		0,                                  /* tp_base */
		0,                                  /* tp_dict */
		0,                                  /* tp_descr_get */
		0,                                  /* tp_descr_set */
		0,                                  /* tp_dictoffset */

		(initproc) VM_init,                 /* tp_init */
		0,                                  /* tp_alloc */
		pyf_VM_new,                         /* tp_new */
		0,                                  /* tp_free */
		0,                                  /* tp_is_gc */
		0,                                  /* tp_bases */
		0,                                  /* tp_mro */
		0,                                  /* tp_cache */
		0,                                  /* tp_subclasses */
		0                                   /* tp_weaklist */
};

/* VMTracker support defs: */
LIFO_LINKED_LIST_DEFINE_BASIC_METHODS_PYALLOC_NOQUAL(VMTracker, VM)
