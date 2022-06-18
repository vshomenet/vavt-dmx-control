#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import hashlib
from classConfig import ConfigHost

path ='/home/sergey/1/'
host = ConfigHost(path)

#c.add_device('Modul-1', 'dimmer', '1', '5')
#print(host.main_menu())


#c.del_device('Modul-1')
#print(c.get_dmx('1'))
#c.set_dmx('1', '1', '0')
#a = c.get_dmx('1')
#for x in a:
#print (x[1].split(', ')[1])import hashlib
data = 'KvBLli'
#hash_object = hashlib.md5(bytes(data, encoding = 'utf-8'))
#a = hash_object.hexdigest()
print(host.passwd('check', data))

