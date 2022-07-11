#!/usr/bin/python3
import os
import sys
import time
import subprocess
import locale
import configparser
import hashlib
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GlobalVar(object):
	def __init__(self):
		self.path = '/media/psf/Home/GIT/vavt-dmx/frontend'
		#self.path = '/opt/dmx'
        
class ConfigHost(object):
	def __init__(self, path):
		self.pathDevice = str(path)+'/conf/device.conf'
		self.pathHost = str(path)+'/conf/host.conf'
		self.pathDMX = str(path)+'/conf/dmx.conf'
		self.main_menu = {"index":"Пресеты", "control":"Ручное управление", "login":"Вход"}
		self.admin_menu = {"index":"Пресеты", "control":"Ручное правление", "config":"Настройки DMX", "cfg_device":"Устройства DMX", \
						   "update":"Обслуживание", "change_admin":"Администратор", "logout":"Выход"}
		self.foot = ['© Сергей Семенов', 'sergey@vshome.net']

	# Пароль и пользователь
	def passwd(self, param, login, passwd):
		def coding (passwd):
			hash_object = hashlib.md5(bytes(passwd, encoding = 'utf-8'))
			return hash_object.hexdigest()
		if param == 'check':
			if coding(login) == self.read_conf('default', 'login'):
				if coding(passwd) == self.read_conf('default', 'pass'):
					return True
			return False
		elif param == 'save':
			self.init_parse(self.pathHost)
			if login:
				self.cfg.set('default', 'login', coding(login))
			if passwd:
				self.cfg.set('default', 'pass', coding(passwd))
			self.write(self.pathHost)

	# чтение конфиг файла
	def read_conf(self, section, param):
		self.init_parse(self.pathHost)
		return self.cfg.get(section, param)

	# Инициализация configparse
	def init_parse(self, path):
		self.cfg = configparser.ConfigParser()
		self.cfg.sections()
		self.cfg.read(path)

	# Запись конфиг файла
	def write(self, path):
		with open(path, 'w') as f:
			self.cfg.write(f)

	# получение всех устройств
	def all_device(self):
		self.init_parse(self.pathDevice)
		return self.cfg.sections()

	# добавление DMX устройств
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
		except:
			return False

	# Удаление устройств
	def del_device(self, device):
		self.init_parse(self.pathDevice)
		self.cfg.remove_section(device)
		self.write(self.pathDevice)

	# Получаем список DMX каналов
	def get_dmx(self, device):
		self.init_parse(self.pathDevice)
		x = self.cfg.items(device)
		del x[0]
		return x

	# Переименование DMX каналов
	def set_dmx(self, device, channel, val):
		self.init_parse(self.pathDevice)
		self.cfg.set(device, channel, val)
		self.write(self.pathDevice)

	# Получаем значения DMX каналов
	def get_dmx_val(self, channel):
		self.init_parse(self.pathDMX)
		return self.cfg.get('manual', channel)

	# Установка значений DMX каналов
	def set_dmx_val(self, channel, val):
		self.init_parse(self.pathDMX)
		self.cfg.set('manual', channel, val)
		self.write(self.pathDMX)

	# Получение всех пресетов
	def get_preset(self):
		self.init_parse(self.pathDMX)
		list_preset = self.cfg.sections()
		del list_preset[0]
		return list_preset

	# Сохранить удалить пресет
	def change_preset(self, val, name):
		self.init_parse(self.pathDMX)
		try:
			if val =='delete':
				self.cfg.remove_section(name)
				self.cfg.write(self.pathDMX)
			if val == 'save':
				pass
		except:
			return False

	# Проверка версии программного обеспечения
	def version(self):
		self.init_parse(self.pathHost)
		return self.read_conf('default', 'version')

	# Вкл Выкл режим debug
	def debug(self):
		self.init_parse(self.pathHost)
		debug = self.read_conf('default', 'debug')
		if debug == 'True' or debug =='true':
			return True
		return False

	# Проверка и обновление системы
	def update(self, com_update):
		os.environ['LC_ALL'] = 'en_US.UTF-8'
		version = self.version()
		def sub (com):
			f = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			res = f.communicate()
			return res
		sub("mkdir /tmp/dmx")
		com_clone = "git clone https://github.com/vshomenet/vavt-dmx-control.git /tmp/dmx"
		clone = sub(com_clone)
		if com_update == "check":
			if not str(clone).find('fatal') >= 0:
				with open('/tmp/dmx/frontend/conf/host.conf', 'r') as f:
					for lines in f.readlines():
						line = lines.strip()
						if line.find('version') >= 0:
							new_version = line.split(' = ')[1]
				if version != new_version:
					res = "Найдена новая версия программного обеспечения " + str(new_version)
				else:
					res = "У вас последняя версия программного обеспечения " + str(version)
			else:
				res = "Сервер обновлений не отвечает"
		if com_update == "update":
			pass
		sub("rm -rf /tmp/dmx")
		return res

