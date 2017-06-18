#   This file defines standard ELF types, structures, and macros.
#   Copyright (C) 1995-2003,2004,2005,2006 Free Software Foundation, Inc.
#   This file is part of the GNU C Library.
#
#   The GNU C Library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   The GNU C Library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with the GNU C Library; if not, write to the Free
#   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#   02111-1307 USA.

from elffile.defines import *
from elffile.elf64_defines import *
import sys, copy, struct
from ctypes import *

#TODO Copy the Elf32 stuff here after it is completed.  Then find and replace the '32_' with '64_'
#TODO remove the Elf32 parts that do not pertain to the Elf 64-bit format