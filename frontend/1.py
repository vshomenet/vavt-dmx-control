#!/usr/bin/python3
import os
import sys
import hashlib
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

host.activate_preset('write', 'manual')
print(host.activate_preset('read'))
