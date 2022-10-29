#!/usr/bin/python3
import socket
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

# Запись ошибок в файл
def write_error(errors):
	for error in errors:
		host.error('write', error, errors[error])
	return

# Вызов суб-процесса
def sub(com):
	f = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	res = f.communicate()
	return res

# Перезагрузка системы
def reboot():
	if host.error('read')[2][1] == 'reboot':
		host.error('write', 'reboot', '')
		time.sleep(0.5)
		os.system('reboot')
	return

# Проверка интернет соединения
def check_network():
	try:
		socket.setdefaulttimeout(1)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((str("8.8.8.8"), int("53")))
		err = ''
		return err
	except socket.error:
		err = 'Нет подключения к интернет'
		return err

# Анализ запущена служба или нет
def check_stat_proc(proc, result):
	error = ''
	if not result[1]:
		res = re.search( r'Active:.+since', str(result[0]))
		if not 'running' in res.group():
			error = 'Служба {proc} не запущена. '.format(proc=proc)
	else:
		error = 'Служба {proc} не установлена или удалена. '.format(proc=proc)
	return error

# Функция поиска ошибок в системе
def check_system():
	error = ''
	sender = sub('systemctl status dmx-sender')
	error += check_stat_proc('dmx-sender', sender)
	#telegram = sub('systemctl status dmx-telegram')
	#error += check_stat_proc('dmx-telegram', telegram)
	return error

# Запуск скрипта
while True:
	errors = dict()
	try:
		reboot()
		time.sleep(0.5)
		errors['error_inet'] = check_network()
		time.sleep(0.5)
		errors['error_sys'] = check_system()
		write_error(errors)
	except:
		time.sleep(2)
