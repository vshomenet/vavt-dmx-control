#!/usr/bin/python3
import os
import sys
import socket
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

def reboot():
	if host.error('read')[2][1] == 'reboot':
		host.error('write', 'reboot', '')
		time.sleep(0.5)
		os.system('reboot')
	return
	
def check_network():
	try:
		socket.setdefaulttimeout(1)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((str("8.8.8.8"), int("53")))
		host.error('write', 'error_inet', '')
		return
	except socket.error:
		host.error('write', 'error_inet', 'Нет подключения к интернет')
		return

while True:
	try:
		reboot()
		time.sleep(0.5)
		check_network()
		time.sleep(0.5)
	except:
		time.sleep(2)
