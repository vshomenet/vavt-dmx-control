#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

for x in host.get_dmx('vika'):
    #print(x[1].split(', ')[0])
    print (x[0])

