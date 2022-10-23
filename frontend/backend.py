#!/usr/bin/python3
import dmx
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

# Получаем DMX значения и формируем посылку
def list_dmx():
	packet = list()
	for dmx in host.get_all_dmx_val(host.activate_preset('read')):
		packet.append(int(dmx[1]))
	return bytes(packet)

# Проверка совместимости и доступности порта
def check_port(*args):
	def sub(com):
		f = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		res = f.communicate()
		return res[0]
	port = args[0]
	if args[1] == 'driver':
		com = 'cat /sys/class/tty/' + port.split('/dev/')[1] + '/device/uevent'
		x = sub(com)
		if x and not 'ftdi' in str(x):
			host.error('write', 'error_back', 'Несовместимое устройство ' + port)
			return False
		return True
	if not sub('ls ' + port):
		host.error('write', 'error_back', 'Не удалось открыть порт ' + port + '. Устройство не найдено.')
		return False
	return True

while True:
	try:
		port = host.read_conf('default', 'dmxsender')
		if not check_port(port, 'driver'):
			x = 1/0
		host.error('write', 'error_back', '')
		sender = dmx.DMX_Serial(port)
		sender.start()
		while True:
			if not check_port(port, ''):
				x = 1/0
			sender.set_data(list_dmx())
			time.sleep(1)
	except Exception as e:
		if str(e) == 'division by zero':
			pass
		elif 'could not open port' in str(e):
			host.error('write', 'error_back', 'Не удалось открыть порт ' + port + '. Устройство не найдено.')
		else:
			host.error('write', 'error_back', 'Неизвестная ошибка: ' + str(e))
		time.sleep(1)

