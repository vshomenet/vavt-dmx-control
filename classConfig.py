#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import configparser
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ConfigDMX(object):
	def __init__(self, path=''):
		self.path = path

	def init_parse(self):
		self.cfg = configparser.ConfigParser()
		self.cfg.sections()
		self.cfg.read(self.path)

	def write(self):
		with open(self.path, 'w') as f:
			self.cfg.write(f)
	
	def all_device(self):
		self.init_parse()
		return self.cfg.sections()

	def add_device(self, device, mode, first_channel, max_channel):
		self.init_parse()
		try:
			self.cfg.add_section(device)
			self.cfg.set(device, 'mode', mode)
			i = int(first_channel)
			while i < int(max_channel)+int(first_channel):
				self.cfg.set(device, str(i), 'channel-'+str(i)+', 0')
				i += 1
			self.write()
			return True
		except:
			return False

	def del_device(self, device):
		self.init_parse()
		self.cfg.remove_section(device)
		self.write()

	def get_dmx(self, device):
		self.init_parse()
		x = self.cfg.items(device)
		del x[0]
		return x

	def set_dmx(self, device, channel, value):
		self.init_parse()
		self.cfg.set(device, channel, value)
		self.write()


'''a = cfg.sections()
print(a)

for x in cfg.sections():
	print(cfg.get(x, 'mode'))
	print(cfg.items(x))
)'''


