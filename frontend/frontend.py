#!/usr/bin/python3
import os
import sys
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, PasswordField, BooleanField, FormField, Form
from wtforms.validators import DataRequired, InputRequired, ValidationError, Email, EqualTo, Length
from werkzeug.exceptions import abort
from classConfig import *

# форма добавить DMX устройство
class addDevice(FlaskForm):
	name_device = StringField(label=('Введите называние устройства:'), validators=[DataRequired()])
	mode_device = RadioField(label=('Укажите режим работы:'), choices=[('dimmer','Режим диммера'),('switch','Режим вкл выкл')], validators=[DataRequired()])
	first_channel = StringField(label=('Укажите первый DMX канал:'), validators=[DataRequired()])
	max_channel = StringField(label=('Укажите сколько DMX каналов на устройстве:'), validators=[DataRequired()])
	save_dev = SubmitField(label=('Сохранить'))

# форма удалить DMX устройство
class delDevice(FlaskForm):
	name_device = RadioField(label=('Какое устройство вы хотите удалить:'), choices=[], validators=[DataRequired()])
	del_dev = SubmitField(label=('Удалить'))

# форма переименовать DMX каналы
class changeNameDMX(FlaskForm):
	list_channel = RadioField(label=('Какой канал вы хотите переименовать:'), choices=[], validators=[DataRequired()])
	name_channel = StringField(label=("Укажите новое имя:"), validators=[DataRequired()])
	save_channel = SubmitField(label=("Сохранить"))

# форма авторизации
class formLogin(FlaskForm):
	login = StringField(label=("Логин"), validators=[DataRequired()])
	passwd = PasswordField('Пароль', validators=[DataRequired()])
	login_btn = SubmitField(label=('Войти'))

# форма смена имени пользователя
class changeAdminName(FlaskForm):
	login = StringField(label=("Логин"), validators=[DataRequired()])
	save_login = SubmitField(label=('Сохранить'))

# форма смены пароля
class changePass(FlaskForm):
	new_pass = PasswordField('Новый пароль', validators=[InputRequired(), Length(min=5, message='Пароль должен быть не меньше %(min)d символов')])
	confirm_pass = PasswordField(label=('Повторите пароль'), validators=[InputRequired(), Length(min=5, message='Пароль должен быть не меньше %(min)d символов')])
	save_pass = SubmitField(label=('Сохранить'))

gv = GlobalVar()
host = ConfigHost(gv.path)
foot = host.foot

secret_key = os.urandom(32)
app = Flask(__name__)
app.config['FLASK_APP'] = "index"
app.config['DEBUG'] = host.debug()
app.config['SECRET_KEY'] = secret_key

#---------- Главная страница ----------
@app.route('/')
def index():
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	page = "Главная страница"
	return render_template("index.html", page = page, menus = menu,  foot = foot)

#---------- Управление ----------
@app.route('/control')
def control():
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	page = "Управление"
	return render_template("control.html", page = page, menus = menu, foot = foot)

#---------- Добавить или удалить DMX устройство ----------
@app.route('/cfg_device', methods=['GET', 'POST'])
def cfg_device():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	page = "Добавить, удалить устройство"
	text = ''
	addDev = addDevice()
	delDev = delDevice()
	delDev.name_device.choices = host.all_device()
	if request.method == 'POST':
		if addDev.save_dev.data:
			name_device = addDev.name_device.data
			mode_device = addDev.mode_device.data
			first_channel = addDev.first_channel.data
			max_channel = addDev.max_channel.data
			if name_device in host.all_device():
				text = "Ошибка сохранения настроек Устройство с таким именем уже есть"
				return render_template("cfg_device.html", page=page, menus=menu, text=text, addDev=addDev, delDev=delDev, foot=foot)
			host.add_device(name_device, mode_device, first_channel, max_channel)
			text = "Настройки сохранены"
		if delDev.del_dev.data and len(host.all_device())>=1:
			name_device = delDev.name_device.data
			host.del_device(name_device)
			return redirect('/cfg_device')
	return render_template("cfg_device.html", page = page, menus = menu, text=text, addDev=addDev, delDev=delDev, foot = foot)

#---------- Переименовать каналы DMX ----------
@app.route('/config', methods=['GET', 'POST'])
def config():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	page = "Настройки"
	return render_template("config.html", page = page, menus = menu, foot = foot)

#---------- Авторизация ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	page = "Авторизация"
	data = 'login'
	text = ''
	lgn = formLogin()
	if request.method == "POST":
		login = lgn.login.data
		passwd = lgn.passwd.data
		if host.passwd('check', login, passwd):
			menu = host.admin_menu
			session['DMXlogin'] = 'admin'
			return redirect(url_for('index'))
	return render_template("admin.html", page = page, menus = menu, data=data, lgn=lgn, foot = foot)

#---------- Смена пароля и имени пользователя ----------
@app.route('/change_admin', methods=['GET', 'POST'])
def change_admin():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	page = "Смена пароля"
	data = 'ch_admin'
	text = ''
	ch_pass = changePass()
	ch_admin = changeAdminName()
	if request.method == "POST":
		if ch_pass.save_pass.data:
			new_pass = ch_pass.new_pass.data
			confirm_pass = ch_pass.confirm_pass.data
			if new_pass == confirm_pass:
				host.passwd('save', None, new_pass)
				text = 'Пароль успешно изменен'
		if ch_admin.login.data:
			login = ch_admin.login.data
			host.passwd('save', login, None)
			text = "Имя пользователя успешно изменено"
	return render_template("admin.html", page = page, menus = menu, text=text, data=data, ch_pass=ch_pass, ch_admin=ch_admin, foot = foot)

#---------- Logout ----------
@app.route('/logout')
def logout():
	session.pop('DMXlogin', None)
	return redirect(url_for('index'))

#---------- Update ----------
# https://github.com/vshomenet/vavt-dmx-control.git
@app.route('/update')
def update():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		pass
	
if __name__ == "__main__":
	app.run()
