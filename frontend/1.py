#!/usr/bin/python3
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

#for x in host.get_dmx('vika'):
#    print(x[1].split(', ')[0])

device = 'test'
mode = 'None'
first_channel = 1
max_channel = 3

host.add_device(device, mode, first_channel, max_channel)
