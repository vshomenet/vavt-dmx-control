#!/usr/bin/python3
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)


#print(host.get_dmx('test'))
#print(host.all_device())
print(host.get_preset())
