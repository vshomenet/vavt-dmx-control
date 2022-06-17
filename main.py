#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from werkzeug.exceptions import abort
from classConfig import ConfigDMX

class addDevice(FlaskForm):
	name_device = StringField(label=('Введите называние устройства:'), validators=[DataRequired()])
	mode_device = RadioField(label=('Укажите режим работы:'), choices=[('dimmer','Режим диммера'),('switch','Режим вкл выкл')], validators=[DataRequired()])
	first_channel = StringField(label=('Укажите первый DMX канал:'), validators=[DataRequired()])
	max_channel = StringField(label=('Укажите сколько DMX каналов на устройстве:'), validators=[DataRequired()])
	save_dev = SubmitField(label=('Сохранить'))

class delDevice(FlaskForm):
	name_device = RadioField(label=('Какое устройство вы хотите удалить:'), choices=[], validators=[DataRequired()])
	del_dev = SubmitField(label=('Удалить'))

secret_key = os.urandom(32)
app = Flask(__name__)
app.config['FLASK_APP'] = "index"
app.config['FLASK_ENV'] = "development"
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = secret_key

device_config ='/home/sergey/1/device.conf'
cfgDMX = ConfigDMX(device_config)

menu = {"index":"Главная", "control":"Управление", "config":"Настройки", "cfg_device":"Устройства"}
foot = "Все права защищены"

@app.route('/')
def index():
	page = "Главная страница"
	return render_template("index.html", page = page, menus = menu,  foot = foot)

@app.route('/control')
def control():
	page = "Управление"
	return render_template("control.html", page = page, menus = menu, foot = foot)

@app.route('/cfg_device', methods=['GET', 'POST'])
def cfg_device():
	page = "Добавить, удалить устройство"
	text = ''
	addDev = addDevice()
	delDev = delDevice()
	delDev.name_device.choices = cfgDMX.all_device()
	if request.method == 'POST':
		if addDev.save_dev.data:
			name_device = addDev.name_device.data
			mode_device = addDev.mode_device.data
			first_channel = addDev.first_channel.data
			max_channel = addDev.max_channel.data
			if name_device in cfgDMX.all_device():
				text = "Ошибка сохранения настроек Устройство с таким именем уже есть"
				return render_template("cfg_device.html", page=page, menus=menu, text=text, addDev=addDev, delDev=delDev, foot=foot)
			cfgDMX.add_device(name_device, mode_device, first_channel, max_channel)
			text = "Настройки сохранены"
		if delDev.del_dev.data and len(cfgDMX.all_device())>=1:
			name_device = delDev.name_device.data
			cfgDMX.del_device(name_device)
			text = 'Устройство удалено'
			return redirect('/cfg_device')
	return render_template("cfg_device.html", page = page, menus = menu, text=text, addDev=addDev, delDev=delDev, foot = foot)

@app.route('/config', methods=['GET', 'POST'])
def config():
	page = "Настройки"
	return render_template("config.html", page = page, menus = menu, foot = foot)

if __name__ == "__main__":
	app.run()
