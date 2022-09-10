#!/usr/bin/python3
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

x = dict()
x['version'] = host.version()
x['debug'] = host.debug()

print(x)
