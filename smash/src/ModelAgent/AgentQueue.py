# MADRiMS
# Copyright (C) 2007  Adam Pridgen < adam.pridgen@gmail.com || atpridgen@mail.utexas.edu >
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from Base import Base
import threading



class AgentQueue(list):
    
    def __init__(self):
        super(AgentQueue, self).__init__()
        self._lock = threading.Lock()
        self._action_on_append = None
        self._action_on_pop = None
    
    def append(self, value):
        self._lock.acquire()
        super(AgentQueue, self).append(value)
        self._lock.release()
                
    def pop(self, int):
        self._lock.acquire()
        value = super(AgentQueue, self).pop(int)
        self._lock.release()
        return value
    

    
        