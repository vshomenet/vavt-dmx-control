#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
from classConfig import ConfigDMX

main_cfg ='/home/sergey/1/config'

c = ConfigDMX(main_cfg)

#c.add_device('Modul-1', 'dimmer', '1', '5')
print(c.all_device())
#c.del_device('Modul-1')
#print(c.get_dmx('1'))
#c.set_dmx('1', '1', '0')
#a = c.get_dmx('1')
#for x in a:
#print (x[1].split(', ')[1])

