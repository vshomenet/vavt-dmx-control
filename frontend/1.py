#!/usr/bin/python3
import os
import sys
import hashlib
import requests
import re
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)
gv.create_conf()

while True:
	gv.log('sergey')
	
'''url = 'http://127.0.0.1:5000/api/v1/dmx'
param = {'preset':'default'}
response = requests.post(url, json=param)
print(response.status_code)
print(response.json())
response = requests.get('http://127.0.0.1:5000/api/v1/dmx/all')
print(response.json())'''
