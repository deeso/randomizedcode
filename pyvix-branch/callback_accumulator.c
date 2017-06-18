/******************************************************************************
 * pyvix - Implementation of VixCallbackAccumulator Type
 * Copyright 2006 David S. Rushby
 * Available under the MIT license (see docs/license.txt for details).
 ****************************************************************************
 * 
 * 
 * Updated 4/22/2008 Adam Pridgen Adam.Pridgen@[foundstone.com || gmail.com]
 * 
 * Added Support for VixCallBack to use tuple.
 * Added accumulators to get Directory, Process, and Shared Folder Information
 * 
 * APIs added:
 * 
 * VixCallbackAccumulator_ListInit - renameed from VixCallbackAccumulator_init
 * VixCallbackAccumulator_TupleInit - add Accumulator Support for tuples
 * VixCallbackAccumulator_accumulateProcessList - info from Listing Processes
 * VixCallbackAccumulator_accumulateDirectoryList - info from Listing Directories
 * VixCallbackAccumulator_accumulateProcessStats - Statistics from running programs/scripts 
 * 
 */

static status VixCallbackAccumulator_ListInit(VixCallbackAccumulator *acc) {
  assert (acc != NULL);

  acc->target = PyList_New(0);
  if (acc->target == NULL) { goto fail; }

  return SUCCEEDED;
  fail:
    assert (PyErr_Occurred());
    return FAILED;
} /* VixCallbackAccumulator_ListInit */

static status VixCallbackAccumulator_TupleInit(VixCallbackAccumulator *acc, unsigned int items) {
  assert (acc != NULL);

  acc->target = PyTuple_New(items);
  if (acc->target == NULL) { goto fail; }

  return SUCCEEDED;
  fail:
    assert (PyErr_Occurred());
    return FAILED;
} /* VixCallbackAccumulator_Tuplenit */


static status VixCallbackAccumulator_clear(VixCallbackAccumulator *acc) {
  assert (acc != NULL);

  Py_CLEAR(acc->target);

  return SUCCEEDED;
} /* VixCallbackAccumulator_clear */

static void VixCallback_accumulateStringList(VixHandle jobH,
    VixEventType eventType, VixHandle eventInfo, void *clientData
  )
{
  PyGILState_STATE gstate;
  PyObject *pyStr = NULL;
  /* Note:  clientData is typically a pointer to memory on another thread's
   * stack, so it's imperative that we refrain from accessing it IN ANY WAY
   * (even just to cast it to VixCallbackAccumulator *acc) until we're sure
   * that the other thread is still waiting for this thread to finish. */
  VixCallbackAccumulator *acc = NULL;

  /* Ignore event types that don't indicate that an item has been found: */
  if (eventType != VIX_EVENTTYPE_FIND_ITEM) { return; }

  ENTER_PYTHON_WITHOUT_CODE_BLOCK(gstate);

  acc = (VixCallbackAccumulator *) clientData;
  assert (acc != NULL);
  assert (acc->target != NULL);
  assert (PyList_CheckExact(acc->target));
  
  assert (eventInfo != VIX_INVALID_HANDLE);
  pyStr = pyf_extractProperty(eventInfo, VIX_PROPERTY_FOUND_ITEM_LOCATION);
  if (pyStr == NULL) { goto fail; }

  if (PyList_Append(acc->target, pyStr) != 0) { goto fail; }

  goto cleanup;
  fail:
    assert (PyErr_Occurred());
    /* Fall through to cleanup: */
  cleanup:
    Py_XDECREF(pyStr);
    LEAVE_PYTHON_WITHOUT_CODE_BLOCK(gstate);
} /* VixCallback_accumulateStringList */

static void VixCallback_accumulateProcessList(VixHandle jobH,
    VixEventType eventType, VixHandle eventInfo, void *clientData
  )
{
  PyGILState_STATE gstate;
  PyObject *pyPName = NULL,
  		   *pyPID = NULL,
  		   *pyOwner = NULL,
  		   *pyCmdLine = NULL,
  		   *pyProcTuple = NULL;

  unsigned int numProcs = 0, index = 0;
  /* Note:  clientData is typically a pointer to memory on another thread's
   * stack, so it's imperative that we refrain from accessing it IN ANY WAY
   * (even just to cast it to VixCallbackAccumulator *acc) until we're sure
   * that the other thread is still waiting for this thread to finish. */
  VixCallbackAccumulator *acc = NULL;

  
  ENTER_PYTHON_WITHOUT_CODE_BLOCK(gstate);
  
  acc = (VixCallbackAccumulator *) clientData;
  assert (acc != NULL);
  assert (acc->target != NULL);
  assert (PyList_CheckExact(acc->target));
  
  
  numProcs = VixJob_GetNumProperties(jobH, VIX_PROPERTY_JOB_RESULT_ITEM_NAME);
  
  for (index = 0; index < numProcs; index++){
	  /* Set these to Null for fail check if necessary */
	  pyProcTuple = NULL;
	  pyPName = NULL;
	  pyPID = NULL;
	  pyCmdLine = NULL;
	  pyOwner = NULL;

	  
	  /* Proc Name */
	  pyPName = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_ITEM_NAME, index);
	  if (pyPName == NULL && 
			  (pyPName = PyString_FromString("Process Command Unknown")) == NULL ) { goto fail; }
	  
	  /* Pid */
	  pyPID = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_PROCESS_ID, index);
	  
	  /* Owner */	  
	  pyOwner = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_PROCESS_OWNER, index);
	  if (pyOwner == NULL && 
			  (pyOwner = PyString_FromString("Process Command Unknown")) == NULL ) { goto fail; }
	  
	  /* Cmd Line */
	  pyCmdLine = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_PROCESS_COMMAND, index);
	  if (pyCmdLine == NULL && 
			  (pyCmdLine = PyString_FromString("Process Command Unknown")) == NULL ) { goto fail; }
	  

	  /* Add Process Items to the Tuple */
	  pyProcTuple = PyTuple_New(4);
	  if (pyProcTuple == NULL) { goto fail; }
	  if (PyTuple_SetItem(pyProcTuple, 0, pyPID) == -1){goto fail;}
	  if (PyTuple_SetItem(pyProcTuple, 1, pyPName) == -1){goto fail;}
	  if (PyTuple_SetItem(pyProcTuple, 2, pyOwner) == -1){goto fail;}
	  if (PyTuple_SetItem(pyProcTuple, 3, pyCmdLine) == -1){goto fail;}
	  
	  /* Add the Tuple to the List */
	  if (PyList_Append(acc->target, pyProcTuple) != 0) { goto fail; }
	  Py_XDECREF(pyProcTuple);
	  
  }
  goto cleanup;
  fail:
    assert (PyErr_Occurred());
    if(pyProcTuple != NULL) {
    	/* pyProcTuple was created successfully, but 
    	 * the failure occurred during list append or
    	 * adding an item.  Since PyTuple_SetItem 'steals'
    	 * references, we only need to XDECREF that object
    	 */
    	Py_XDECREF(pyProcTuple);
    }else{
    	if(pyPID != NULL) { Py_XDECREF(pyPID); }
    	if(pyPName != NULL) { Py_XDECREF(pyPName); }
    	if(pyOwner != NULL) { Py_XDECREF(pyOwner); }
    	if(pyCmdLine != NULL) { Py_XDECREF(pyCmdLine); }
    }
    /* Fall through to cleanup: */
  cleanup:
    LEAVE_PYTHON_WITHOUT_CODE_BLOCK(gstate);
} /* VixCallback_accumulateProcessList */



static void VixCallback_accumulateDirectoryList(VixHandle jobH,
    VixEventType eventType, VixHandle eventInfo, void *clientData
  )
{
  PyGILState_STATE gstate;
  PyObject *pyFName = NULL,
  		   *pyFFlags = NULL,
  		   *pyFileProps = NULL;

  unsigned int numDirs = 0, index = 0;
  /* Note:  clientData is typically a pointer to memory on another thread's
   * stack, so it's imperative that we refrain from accessing it IN ANY WAY
   * (even just to cast it to VixCallbackAccumulator *acc) until we're sure
   * that the other thread is still waiting for this thread to finish. */
  VixCallbackAccumulator *acc = NULL;

  
  ENTER_PYTHON_WITHOUT_CODE_BLOCK(gstate);
  
  acc = (VixCallbackAccumulator *) clientData;
  assert (acc != NULL);
  assert (acc->target != NULL);
  assert (PyList_CheckExact(acc->target));
  //assert (eventInfo != VIX_INVALID_HANDLE);
  
  numDirs = VixJob_GetNumProperties(jobH, VIX_PROPERTY_JOB_RESULT_ITEM_NAME);
  for (index = 0; index < numDirs; index++){
	  /* Set these to Null for fail check if necessary */
	  pyFName = NULL;
	  pyFFlags = NULL;
	  pyFileProps = NULL;
	  
	  /* File Name */
	  pyFName = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_ITEM_NAME, index);
	  if (pyFName == NULL && 
			  (pyFName = PyString_FromString("Process Command Unknown")) == NULL ) { goto fail; }
	  /* File Name */
	  pyFFlags = pyf_extractNthProperty(jobH, VIX_PROPERTY_JOB_RESULT_FILE_FLAGS, index);
	  if (pyFFlags == NULL && 
			  (pyFFlags = PyString_FromString("Process Command Unknown")) == NULL ) { goto fail; }
	  
	  /* Add Process Items to the Tuple */
	  pyFileProps= PyTuple_New(2);
	  if (pyFileProps == NULL) { goto fail; }
	  if (PyTuple_SetItem(pyFileProps, 0, pyFName) == -1){goto fail;}
	  if (PyTuple_SetItem(pyFileProps, 1, pyFFlags) == -1){goto fail;}
	  	  
	  /* Add the File Name to the List */
	  if (PyList_Append(acc->target, pyFileProps) != 0) { goto fail; }
	  Py_XDECREF(pyFileProps);	  
  }
  
  goto cleanup;
  fail:
    assert (PyErr_Occurred());
    if(pyFileProps != NULL) { Py_XDECREF(pyFileProps); }
    else{
	    if(pyFName != NULL) { Py_XDECREF(pyFName); }
	    if(pyFFlags != NULL) { Py_XDECREF(pyFFlags); }
    }
    /* Fall through to cleanup: */
  cleanup:
    LEAVE_PYTHON_WITHOUT_CODE_BLOCK(gstate);
} /* VixCallback_accumulateDirectoryList */

static void VixCallback_accumulateSharedStateList(VixHandle jobH,
    VixEventType eventType, VixHandle eventInfo, void *clientData
  )
{
  PyGILState_STATE gstate;
  PyObject *pyFName = NULL,
  		   *pyHostPath = NULL,
  		   *pyFolderFlags = NULL;

  
  /* Note:  clientData is typically a pointer to memory on another thread's
   * stack, so it's imperative that we refrain from accessing it IN ANY WAY
   * (even just to cast it to VixCallbackAccumulator *acc) until we're sure
   * that the other thread is still waiting for this thread to finish. */
  VixCallbackAccumulator *acc = NULL;

  
  ENTER_PYTHON_WITHOUT_CODE_BLOCK(gstate);
  
  acc = (VixCallbackAccumulator *) clientData;
  assert (acc != NULL);
  assert (acc->target != NULL);
  assert (PyTuple_CheckExact(acc->target));
  assert (PyTuple_Size(	acc->target) == 3);
  
  pyFName = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_ITEM_NAME);
  if (pyFName == NULL) { goto fail; }
  			
  pyHostPath = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_HOST);
  if (pyHostPath == NULL) { goto fail; }
  
  pyFolderFlags = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_SHARED_FOLDER_FLAGS);
  if (pyFolderFlags == NULL) { goto fail; }
  
  /* Add the item, then set the object to NULL
   * since PyTuple steals the reference.  In case
   * of a failure this keeps XDECREF from over 
   * decrementing references once they are in the 
   * tuple object
   */
  if (PyTuple_SetItem(acc->target, 0, pyFName) == -1){goto fail;}
  pyFName = NULL;
  if (PyTuple_SetItem(acc->target, 1, pyHostPath) == -1){goto fail;}
  pyHostPath = NULL;
  if (PyTuple_SetItem(acc->target, 2, pyFolderFlags) == -1){goto fail;}
  pyFolderFlags = NULL;
  
  
  
  
  goto cleanup;
  fail:
    assert (PyErr_Occurred());
    if (pyFName != NULL) { Py_XDECREF(pyFName); }
    if (pyHostPath != NULL) { Py_XDECREF(pyHostPath); }
    if (pyFolderFlags != NULL) { Py_XDECREF(pyFolderFlags); }
      
    /* Fall through to cleanup: */
  cleanup:
    LEAVE_PYTHON_WITHOUT_CODE_BLOCK(gstate);
} /* VixCallback_accumulateSharedFolderState */
static void VixCallback_accumulateProcessStats(VixHandle jobH,
    VixEventType eventType, VixHandle eventInfo, void *clientData
  )
{
  PyGILState_STATE gstate;
  PyObject *pyPID = NULL,
  		   *pyElapsedTime = NULL,
  		   *pyExitCode = NULL;

  
  /* Note:  clientData is typically a pointer to memory on another thread's
   * stack, so it's imperative that we refrain from accessing it IN ANY WAY
   * (even just to cast it to VixCallbackAccumulator *acc) until we're sure
   * that the other thread is still waiting for this thread to finish. */
  VixCallbackAccumulator *acc = NULL;

  
  ENTER_PYTHON_WITHOUT_CODE_BLOCK(gstate);
  
  acc = (VixCallbackAccumulator *) clientData;
  assert (acc != NULL);
  assert (acc->target != NULL);
  assert (PyTuple_CheckExact(acc->target));
  assert (PyTuple_Size(	acc->target) == 3);
  
  pyPID = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_PROCESS_ID);
  if (pyPID == NULL) { goto fail; }
  			
  pyElapsedTime = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_GUEST_PROGRAM_ELAPSED_TIME);
  if (pyElapsedTime == NULL) { goto fail; }
  
  pyExitCode = pyf_extractProperty(jobH, VIX_PROPERTY_JOB_RESULT_GUEST_PROGRAM_EXIT_CODE);
  if (pyExitCode == NULL) { goto fail; }
  
  /* Add the item, then set the object to NULL
   * since PyTuple steals the reference.  In case
   * of a failure this keeps XDECREF from over 
   * decrementing references once they are in the 
   * tuple object
   */
  if (PyTuple_SetItem(acc->target, 0, pyPID) == -1){goto fail;}
  pyPID = NULL;
  if (PyTuple_SetItem(acc->target, 1, pyElapsedTime) == -1){goto fail;}
  pyElapsedTime = NULL;
  if (PyTuple_SetItem(acc->target, 2, pyExitCode) == -1){goto fail;}
  pyExitCode = NULL;
  
  goto cleanup;
  fail:
    assert (PyErr_Occurred());
    if (pyPID != NULL) { Py_XDECREF(pyPID); }
    if (pyElapsedTime != NULL) { Py_XDECREF(pyElapsedTime); }
    if (pyExitCode != NULL) { Py_XDECREF(pyExitCode); }
      
    /* Fall through to cleanup: */
  cleanup:
    LEAVE_PYTHON_WITHOUT_CODE_BLOCK(gstate);
} /* VixCallback_accumulateSharedFolderState */
