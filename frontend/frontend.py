#!/usr/bin/python3
import os
import sys
import time
import subprocess
from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, PasswordField, BooleanField, FormField, Form, DecimalRangeField, IntegerRangeField
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

# выбор DMX прибора для переименования каналов
class selectChangeDMX(FlaskForm):
	list_dmx = RadioField(label=('Какой прибор вы хотите редактировать:'), choices=[], validators=[DataRequired()])
	sel_dmx = SubmitField(label=('Выбрать'))

# форма переименовать DMX каналы
class changeNameDMX(FlaskForm):
	list_channel = RadioField(label=('Какой канал вы хотите переименовать:'), choices=[], validators=[DataRequired()])
	name_channel = StringField(label=('Укажите новое имя:'))
	save_channel = SubmitField(label=('Сохранить'))
	finish_edit = SubmitField(label=('Закончить редактировать'))

# форма управления DMX
class controlDMX(FlaskForm):
	list_device = RadioField(label=('Каким прибором вы хотите управлять:'), choices=[], validators=[DataRequired()])
	select_device = SubmitField(label=('Выбрать'))
	save_dmx = SubmitField(label=('Отправить'))
	finish_control = SubmitField(label=('Выбрать другой'))

# форма сохранить пресет
class savePreset(FlaskForm):
	name_preset = StringField(label=('Введите название'), validators=[DataRequired()])
	save_preset = SubmitField(label=('Сохранить'))

# форма вызов пресета и удаление
class activePreset(FlaskForm):
	list_preset = RadioField(label=('Какой пресет необходимо загрузить:'), choices=[], validators=[DataRequired()])
	active_preset = SubmitField(label=('Загрузить'))
	del_preset = SubmitField(label=('Удалить'))

# форма сброса всех значений dmx на 0
class formBlack(FlaskForm):
	black = SubmitField('Сброс')

# форма авторизации
class formLogin(FlaskForm):
	login = StringField(label=('Логин'), validators=[DataRequired()])
	passwd = PasswordField('Пароль', validators=[DataRequired()])
	login_btn = SubmitField(label=('Войти'))

# форма смена имени пользователя
class changeAdminName(FlaskForm):
	login = StringField(label=('Новый логин'), validators=[DataRequired()])
	save_login = SubmitField(label=('Сохранить'))

# форма смены пароля
class changePass(FlaskForm):
	new_pass = PasswordField('Новый пароль', validators=[InputRequired(), Length(min=5, message='Пароль должен быть не меньше %(min)d символов')])
	confirm_pass = PasswordField(label=('Повторите пароль'), validators=[InputRequired(), Length(min=5, message='Пароль должен быть не меньше %(min)d символов')])
	save_pass = SubmitField(label=('Сохранить'))

# Форма проверки обновлений
class formUpdate(FlaskForm):
	check_update = SubmitField('Проверить')
	update = SubmitField('Обновить')

def api_parse(key, param):
	if key in ['preset']:
		if key == 'preset' and param in ['default'] + host.get_preset():
			host.activate_preset('write', param)
			return True
	return False
	
gv = GlobalVar()
host = ConfigHost(gv.path)
foot = host.foot
foot.append("Версия программного обеспечения "+host.version())
foot.append("ID установки " + host.id_install())

secret_key = os.urandom(32)
app = Flask(__name__)
app.config['FLASK_APP'] = "index"
app.config['DEBUG'] = host.debug()
app.config['SECRET_KEY'] = secret_key

#---------- Главная страница ----------
@app.route('/', methods=['GET', 'POST'])
def index():
	if not "DMXlogin" in session:
		menu = host.main_menu
		form = ''
	else:
		menu = host.admin_menu
		form = 'admin'
	page = "Пресеты"
	text = 'Загружен пресет ' + host.activate_preset('read')
	data = ''
	aPr = activePreset()
	sPr = savePreset()
	aPr.list_preset.choices = ['default'] + host.get_preset()
	if request.method == 'POST':
		if aPr.active_preset.data:
			data = aPr.list_preset.data
			host.activate_preset('write', data)
			return redirect(url_for('index'))
		if aPr.del_preset.data:
			data = aPr.list_preset.data
			if data != 'default':
				host.change_preset('delete', data, None)
				host.activate_preset('write', 'default')
				return redirect(url_for('index'))
			else:
				text = 'Нельзя удалить системный пресет default'
		if sPr.name_preset.data:
			data =  sPr.name_preset.data
			host.change_preset('save', data, host.activate_preset('read'))
			#host.activate_preset('write', data)
			return redirect(url_for('index'))
	return render_template("preset.html", page = page, text = text, menus = menu, form = form, aPr=aPr, sPr = sPr, foot = foot)

#---------- Управление ----------
@app.route('/control', methods=['GET', 'POST'])
def control():
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	page = "Ручное управление"
	form = 'select_device'
	text = ''
	mode = ''
	text2 = 'Загружен пресет ' + host.activate_preset('read')
	data = host.all_device()
	cDMX = controlDMX()
	fBl = formBlack()
	cDMX.list_device.choices = host.all_device()
	if 'DMXcontrol' in session:
		form = 'control_device'
		device = session['DMXcontrol']
		text = 'Вы управляете прибором '+device
		mode = host.get_mode(device)
		data = host.get_dmx(device)
	if request.method == 'POST':
		if cDMX.select_device.data:
			device = cDMX.list_device.data
			session['DMXcontrol'] = device
			return redirect(url_for('control'))
		if cDMX.finish_control.data:
			session.pop('DMXcontrol', None)
			return redirect(url_for('control'))
		if fBl.black.data:
			host.dmx_reset(host.read_conf('default', 'preset'))
			return redirect(url_for('control'))
		val = request.form
		for ch_dmx in val:
			if len(ch_dmx) < 4:
				host.set_dmx_val(host.read_conf('default', 'preset'), ch_dmx, val[ch_dmx])
		return redirect(url_for('control'))
	return render_template("control.html", page = page, text = text, text2=text2, menus = menu, form = form, data = data, cDMX = cDMX, fBl=fBl, host=host, mode=mode, foot = foot)

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
			return redirect(url_for('cfg_device'))
		if delDev.del_dev.data and len(host.all_device())>=1:
			name_device = delDev.name_device.data
			session.pop('DMXdevice', None)
			session.pop('DMXcontrol', None)
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
	page = "Переименование DMX каналов в приборах"
	text = ''
	form = 'select_device'
	selDMX = selectChangeDMX()
	changeDMX = changeNameDMX()
	selDMX.list_dmx.choices = host.all_device()
	if 'DMXdevice' in session:
		form = 'change_device'
		device = session['DMXdevice']
		text = 'Вы редактируете прибор '+device
		changeDMX.list_channel.choices = host.get_dmx(device)
	if request.method =='POST':
		if selDMX.sel_dmx.data:
			name_device = selDMX.list_dmx.data
			session['DMXdevice'] = name_device
			return redirect(url_for('config'))
		if changeDMX.save_channel.data:
			name_channel = changeDMX.name_channel.data
			num_channel = changeDMX.list_channel.data
			if not name_channel:
				name_channel = 'None'
			host.set_dmx(device, num_channel, name_channel)
			return redirect(url_for('config'))
		if changeDMX.finish_edit.data:
			session.pop('DMXdevice', None)
			return redirect(url_for('config'))
	return render_template("config.html", page = page, form = form, text = text, selDMX = selDMX, changeDMX = changeDMX, menus = menu, foot = foot)

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
	page = "Смена имени пользователя и пароля"
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
@app.route('/update', methods=['GET', 'POST'])
def update():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		page = "Обновление системы"
		menu = host.admin_menu
	upd = formUpdate()
	text = ''
	f = 'false'
	if request.method == "POST":
		if upd.check_update.data:
			text = host.update('check')
			if 'update' in text:
				f = 'true'
		if upd.update.data:
			host.update('update')
			return redirect(url_for('upgrade'))
	return render_template("update.html", page = page, menus = menu, text = text, upd = upd, f=f,  foot = foot)
	
#---------- Upgrade ----------
@app.route('/upgrade')
def upgrade():
	return render_template("upgrade.html")

#---------- Error 404 ----------
@app.errorhandler(404)
def page_not_found(e):
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	page = ''
	return render_template('404.html', page = page, menus = menu,  foot = foot), 404

#---------- API ----------
@app.route('/api/v1/dmx/<string:param>', methods=['GET'])
def api_info(param):
	api = dict()
	api['uuid'] = host.id_install()
	api['version'] = host.version()
	api['debug'] = host.debug()
	api['mode'] = host.read_conf('default', 'mode')
	api['preset'] = host.read_conf('default', 'preset')
	api['dmxsender'] = host.read_conf('default', 'dmxsender')
	api['device'] = host.all_device()
	api['all_preset'] = ['default'] + host.get_preset()
	if param == 'all':
		return jsonify(api)
	elif param in api:
		return jsonify({param : api[param]})
	return jsonify({'error':'param '+str(param)+' not found'})

@app.route('/api/v1/dmx', methods=['POST'])
def api_control():
	if request.json:
		key = list(request.json.keys())[0]
		if api_parse(key, request.json[key]):
			return jsonify({'dmx':'success'}), 201
	return jsonify({'error':'incorrect json request'})

#---------- Temp Backdoor ----------
@app.route('/log')
def log():
	session['DMXlogin'] = 'admin'
	return redirect(url_for('index')) #'''

if __name__ == "__main__":
	app.run()
