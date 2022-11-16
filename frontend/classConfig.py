#!/usr/bin/python3
import os
import sys
import time
import subprocess
import locale
import configparser
import hashlib
import base64
import random
import uuid
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GlobalVar(object):
	def __init__(self):
		#self.path = '/media/psf/Home/GIT/vavt-dmx/frontend'
		self.path = '/opt/dmx'
		
	# Копирование файла sys.conf в оперативную память
	def create_conf(self):
		if not os.path.isfile('/dev/shm/sys.conf'):
			os.system('cp '+self.path+'/conf/sys.conf /dev/shm/')
        
class ConfigHost(object):
	def __init__(self, path):
		self.pathDevice = str(path)+'/conf/device.conf'
		self.pathHost = str(path)+'/conf/host.conf'
		self.pathDMX = str(path)+'/conf/dmx.conf'
		self.pathSys = '/dev/shm/sys.conf'
		self.main_menu = {"index":"Пресеты", "control":"Ручное управление", "login":"Вход"}
		self.admin_menu = {"index":"Пресеты", "control":"Ручное правление", "config":"Настройки DMX", "cfg_device":"Устройства DMX", \
						   "telegram":"Telegram", "update":"Обслуживание", "change_admin":"Администратор", "logout":"Выход"}
		self.foot = ['© Сергей Семенов sergey@vshome.net']

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
		
	# получение режима работы прибора
	def get_mode(self, device):
		self.init_parse(self.pathDevice)
		return self.cfg.get(device, 'mode')

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
	def get_dmx_val(self, preset, channel):
		self.init_parse(self.pathDMX)
		return self.cfg.get(preset, channel)
		
	# Получаем список всех DMX каналов и их значения
	def get_all_dmx_val(self, preset):
		self.init_parse(self.pathDMX)
		return self.cfg.items(preset)

	# Установка значений DMX каналов
	def set_dmx_val(self, preset, channel, val):
		self.init_parse(self.pathDMX)
		self.cfg.set(preset, channel, val)
		self.write(self.pathDMX)
		
	# Сброс всех DMX на 0
	def dmx_reset(self, preset):
		self.init_parse(self.pathDMX)
		i = 1
		while i < 513:
			self.cfg.set(preset, str(i), '0')
			i += 1
		self.write(self.pathDMX)

	# Получение всех пресетов
	def get_preset(self):
		self.init_parse(self.pathDMX)
		list_preset = self.cfg.sections()
		del list_preset[0]
		return list_preset

	# Сохранить удалить пресет
	def change_preset(self, val, name, old_preset):
		self.init_parse(self.pathDMX)
		try:
			if val =='delete':
				self.cfg.remove_section(name)
				self.write(self.pathDMX)
			if val == 'save':
				if not name in self.get_preset():
					self.cfg.add_section(name)
					self.write(self.pathDMX)
				channel = 1
				while channel < 513:
					data = self.cfg.get(old_preset, str(channel))
					self.cfg.set(name, str(channel), data)
					channel += 1
				self.write(self.pathDMX)
			return True
		except Exception as e:
			#print(e)
			return False
	
	# Активация пресета
	def activate_preset(self, *args):
		self.init_parse(self.pathHost)
		if args[0] == 'read':
			return self.read_conf('default', 'preset')
		elif args[0] == 'write':
			self.cfg.set('default', 'preset', args[1])
			self.write(self.pathHost)

	# Проверка версии программного обеспечения
	def version(self):
		self.init_parse(self.pathSys)
		return self.cfg.get('default', 'version')
		
	# Сссылка на проект
	def url(self):
		self.init_parse(self.pathSys)
		return self.cfg.get('default', 'url')
	
	# UUID установки
	def id_install(self):
		with open('/etc/machine-id', 'r') as f:
			for line in f:
				if len(line) > 3:
					os_uuid = line
		id = str(uuid.uuid3(uuid.NAMESPACE_X500, str(uuid.getnode())+os_uuid))
		return id

	# Чтение и запись ошибок
	def error(self, *args):
		self.init_parse(self.pathSys)
		if args[0] is 'read':
			return self.cfg.items('default')
		if args[0] is 'write':
			self.cfg.set('default', args[1], args[2])
			self.write(self.pathSys)
			return None
		
	# Telegram token, пользователи чтение запись
	def telegram(self, *args):
		self.init_parse(self.pathHost)
		if args[0] == 'read_token':
			return self.cfg.get('telegram', 'token')
		elif args[0] == 'write_token':
			self.cfg.set('telegram', 'token', args[1])
			self.write(self.pathHost)
		elif args[0] == 'del_token':
			self.cfg.set('telegram', 'token', '')
			self.write(self.pathHost)
		elif args[0] == 'all_users':
			users = self.cfg.items('telegram')
			del users[0]
			return users
		elif args[0] == 'add_user':
			self.cfg.set('telegram', args[1], args[2])
			self.write(self.pathHost)
		elif args[0] == 'del_user':
			self.cfg.remove_option('telegram', args[1])
			self.write(self.pathHost)
			return
		
	# Вкл Выкл режим debug
	def debug(self):
		self.init_parse(self.pathSys)
		debug = self.cfg.get('default', 'debug')
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
		def check_ver():
			res = list()
			if not str(clone).find('fatal') >= 0:
				with open('/tmp/dmx/frontend/conf/sys.conf', 'r') as f:
					for lines in f.readlines():
						line = lines.strip()
						if line.find('version') >= 0:
							new_version = line.split(' = ')[1]
				if version != new_version:
					res.append("Найдена новая версия программного обеспечения " + str(new_version))
					res.append('update')
				else:
					res.append("У вас последняя версия программного обеспечения " + str(version))
			else:
				res.append("Сервер обновлений не отвечает")
			return res
		if com_update == "check":
			if os.path.exists("/tmp/dmx"):
				sub("rm -rf /tmp/dmx")
			sub("mkdir /tmp/dmx")
			com_clone = "git clone " + self.url() + ".git /tmp/dmx"
			clone = sub(com_clone)
			res = check_ver()
		if com_update == "update":
			if os.path.exists("/tmp/dmx"):
				f = subprocess.Popen('/tmp/dmx/frontend/update.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			res = []
		return res

