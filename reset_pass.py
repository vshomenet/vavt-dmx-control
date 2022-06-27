#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import random
import string
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)

valid_letters='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
login = 'admin'
i = 0
secret_key = ''
while i < 6 :
	secret_key += random.choice(valid_letters)
	i+=1
host.passwd('save', login, secret_key)
print("Пароль сброшен.\nИмя пользователя: admin\nПароль:", secret_key)

