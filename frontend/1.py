#!/usr/bin/python3
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

#for x in host.get_dmx('vika'):
#    print(x[1].split(', ')[0])

print(host.all_device())

print(host.get_dmx('test'))
print(host.get_dmx('test-2'))

print(host.get_dmx_val('1'))
