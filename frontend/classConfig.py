#!/usr/bin/python3
import os
import sys
import configparser
import hashlib
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class GlobalVar(object):
    def __init__(self):
        self.path = '/media/psf/Home/GIT/vavt-dmx/frontend'
        
class ConfigHost(object):
	def __init__(self, path):
		self.pathDevice = str(path)+'/conf/device.conf'
		self.pathHost = str(path)+'/conf/host.conf'
		self.pathDMX = str(path)+'/conf/dmx.conf'
		self.main_menu = {"index":"Главная", "control":"Управление", "login":"Вход"}
		self.admin_menu = {"index":"Главная", "control":"Управление", "config":"Настройки DMX", "cfg_device":"Устройства DMX", "change_admin":"Администратор"}
		self.foot = "Все права защищены"

	def passwd(self, param, login, passwd):
		def coding (passwd):
			hash_object = hashlib.md5(bytes(passwd, encoding = 'utf-8'))
			return hash_object.hexdigest()
		if param == 'check':
			if coding(login) == self.read_conf('default', 'login'):
				if coding(passwd) == self.read_conf('default', 'pass'):
					return True
			return False
		elif param == 'coding':
			return coding(passwd)
		elif param == 'save':
			self.init_parse(self.pathHost)
			if login:
				self.cfg.set('default', 'login', coding(login))
			if passwd:
				self.cfg.set('default', 'pass', coding(passwd))
			self.write(self.pathHost)

	def read_conf(self, section, param):
		self.init_parse(self.pathHost)
		return self.cfg.get(section, param)
		
	def init_parse(self, path):
		self.cfg = configparser.ConfigParser()
		self.cfg.sections()
		self.cfg.read(path)

	def write(self, path):
		with open(path, 'w') as f:
			self.cfg.write(f)
	
	def all_device(self):
		self.init_parse(self.pathDevice)
		return self.cfg.sections()

	def add_device(self, device, mode, first_channel, max_channel):
		self.init_parse(self.pathDevice)
		try:
			self.cfg.add_section(device)
			self.cfg.set(device, 'mode', mode)
			i = int(first_channel)
			while i < int(max_channel)+int(first_channel):
				self.cfg.set(device, str(i), 'channel-'+str(i))
				i += 1
			self.write(self.pathDevice)
			return True
		except Exception as e:
			print(e)
			return False

	def del_device(self, device):
		self.init_parse(self.pathDevice)
		self.cfg.remove_section(device)
		self.write(self.pathDevice)

	def get_dmx(self, device):
		self.init_parse(self.pathDevice)
		x = self.cfg.items(device)
		del x[0]
		return x

	def set_dmx(self, device, channel, value):
		self.init_parse(self.pathDevice)
		self.cfg.set(device, channel, value)
		self.write(self.pathDevice)

	def debug(self):
		self.init_parse(self.pathHost)
		debug = self.read_conf('default', 'debug')
		if debug == 'True' or debug =='true':
			return True
		return False

'''a = cfg.sections()
print(a)

for x in cfg.sections():
	print(cfg.get(x, 'mode'))
	print(cfg.items(x))
)'''


