#!/usr/bin/python3
import os
import sys
import time
import subprocess
from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, PasswordField, BooleanField, FormField, Form, DecimalRangeField, IntegerRangeField
from wtforms.validators import DataRequired, InputRequired, ValidationError, Email, EqualTo, Length
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
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
	reset = SubmitField('Перезапустить')
	reboot = SubmitField('Перезагрузить')
	
# Форма добавить token telegram
class formTokenTelegram(FlaskForm):
	name_token = StringField(label=('Введите token вашего телеграм бота:'), validators=[DataRequired()])
	save_token = SubmitField(label=('Сохранить'))
	
# Форма удалить токен telegram
class formDelTokenTelegram(FlaskForm):
	del_token = SubmitField(label=('Удалить'))

# Форма добавить пользователя telegram
class formAddUserTelegram(FlaskForm):
	name_user = StringField(label=('Введите имя пользователя:'), validators=[DataRequired()])
	name_id = StringField(label=('Введите ID пользователя:'), validators=[DataRequired()])
	save_user = SubmitField(label=('Сохранить'))

# Форма удалить пользователя telegram
class formDelUserTelegram(FlaskForm):
	name_user = RadioField(label=('Какого пользователя вы хотите удалить:'), choices=[], validators=[DataRequired()])
	del_user = SubmitField(label=('Удалить'))

# Парсинг запроса API активация пресета
def api_parse(data, ip):
	try:
		if host.passwd('check', data['login'], data['pass']):
			if data['system'].lower() in ['reset', 'reboot']:
				if data['system'].lower() == 'reset':
					gv.log(f'[warning] [api] User {ip} started restart all services')
					gv.restart()
				if data['system'].lower() == 'reboot':
					gv.log(f'[warning] [api] User {ip} started reboot system')
					host.error('write', 'reboot', 'reboot')
				reply = {'DMX':'A {} command has been sent to the system'.format(data['system'])}
				return reply
			if data['preset'] in ['default'] + host.get_preset():
				host.activate_preset('write', data['preset'])
				gv.log(f"[info] [api] User {ip} activated preset {data['preset']}")
				reply = {'DMX':'Preset {} activated'.format(data['preset'])}
			else:
				gv.log(f"[info] [api] User {ip} requested incorrect preset {data['preset']}")
				reply = {'Error':'Preset {} not found'.format(data['preset'])}
		else:
			gv.log(f'[error] [api] User {ip} sended incorrect login or password')
			reply = {'Error':'Incorrect login or password'}
		return reply
	except:
		gv.log(f'[warning] [api] User {ip} sended incorrect json request')
		reply = {'Error':'Incorrect json request'}
		return reply

# Проверка файла buckup на соответствие
def check_backup(filename):
	name = filename.split('.')
	if len(name) > 1:
		if name[1] == 'dmx':
			return True
	return False
	
gv = GlobalVar()
host = ConfigHost(gv.path)
foot = host.foot
foot.append('ID установки ' + host.id_install())
host.check_conf('default')
gv.create_conf()
url = host.url()

upload_folder = gv.path + '/download'
secret_key = os.urandom(32)
app = Flask(__name__)
app.config['FLASK_APP'] = 'index'
app.config['DEBUG'] = host.debug()
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = upload_folder

#---------- Главная страница ----------
@app.route('/', methods=['GET', 'POST'])
def index():
	if not "DMXlogin" in session:
		menu = host.main_menu
		form = ''
	else:
		menu = host.admin_menu
		form = 'admin'
	ip = request.remote_addr
	page = 'Пресеты'
	text = 'Загружен пресет ' + host.activate_preset('read')
	data = ''
	aPr = activePreset()
	sPr = savePreset()
	aPr.list_preset.choices = ['default'] + host.get_preset()
	if request.method == 'POST':
		if aPr.active_preset.data:
			data = aPr.list_preset.data
			host.activate_preset('write', data)
			gv.log(f'[info] [web] User {ip} activated preset {data}')
			return redirect(url_for('index'))
		if aPr.del_preset.data:
			data = aPr.list_preset.data
			if data != 'default':
				host.change_preset('delete', data, None)
				host.activate_preset('write', 'default')
				gv.log(f'[warning] [web] User {ip} deleted preset {data}')
				return redirect(url_for('index'))
			else:
				text = 'Нельзя удалить системный пресет default'
		if sPr.name_preset.data:
			data =  sPr.name_preset.data
			if data in ['reset', 'reboot', 'default']:
				text = f'Название пресета не может быть {data}, это имя зарезервировано системой'
				return render_template("preset.html", page = page, text = text, menus = menu, form = form, aPr=aPr, sPr = sPr, foot = foot, url = url)
			host.change_preset('save', data, host.activate_preset('read'))
			gv.log(f'[info] [web] User {ip} created new preset {data}')
			#host.activate_preset('write', data)
			return redirect(url_for('index'))
	return render_template("preset.html", page = page, text = text, menus = menu, form = form, aPr=aPr, sPr = sPr, foot = foot, url = url)

#---------- Управление ----------
@app.route('/control', methods=['GET', 'POST'])
def control():
	if not "DMXlogin" in session:
		menu = host.main_menu
		f = ''
	else:
		menu = host.admin_menu
		f = 'admin'
	ip = request.remote_addr
	page = 'Ручное управление'
	form = 'select_device'
	text = ''
	mode = ''
	text2 = 'Вы редактируете пресет ' + host.activate_preset('read')
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
			gv.log(f"[warning] [web] User {ip} reset DMX on zero in preset {host.read_conf('default', 'preset')}")
			return redirect(url_for('control'))
		val = request.form
		dmx = list()
		for ch_dmx in val:
			if len(ch_dmx) < 4:
				dmx.append(ch_dmx)
				host.set_dmx_val(host.read_conf('default', 'preset'), ch_dmx, val[ch_dmx])
		gv.log(f"[info] [web] User {ip} changed value DMX channels {', '.join(dmx)} in preset {host.read_conf('default', 'preset')}")
		return redirect(url_for('control'))
	return render_template("control.html", page = page, text = text, text2=text2, menus = menu, f=f, form = form, data = data, cDMX = cDMX, fBl=fBl, host=host, mode=mode, foot = foot, url = url)

#---------- Добавить или удалить DMX устройство ----------
@app.route('/cfg_device', methods=['GET', 'POST'])
def cfg_device():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	page = 'Добавить, удалить устройство'
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
				text = 'Ошибка сохранения настроек Устройство с таким именем уже есть'
				return render_template("cfg_device.html", page=page, menus=menu, text=text, addDev=addDev, delDev=delDev, foot=foot, url = url)
			host.add_device(name_device, mode_device, first_channel, max_channel)
			gv.log(f'[info] [web] User {ip} added new device {name_device}')
			return redirect(url_for('cfg_device'))
		if delDev.del_dev.data and len(host.all_device())>=1:
			name_device = delDev.name_device.data
			session.pop('DMXdevice', None)
			session.pop('DMXcontrol', None)
			host.del_device(name_device)
			gv.log(f'[warning] [web] User {ip} deleted device {name_device}')
			return redirect('/cfg_device')
	return render_template("cfg_device.html", page = page, menus = menu, text=text, addDev=addDev, delDev=delDev, foot = foot, url = url)

#---------- Переименовать каналы DMX ----------
@app.route('/config', methods=['GET', 'POST'])
def config():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	page = 'Переименование DMX каналов в приборах'
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
			gv.log(f'[info] [web] User {ip} changed name channels {num_channel} in device {device}')
			return redirect(url_for('config'))
		if changeDMX.finish_edit.data:
			session.pop('DMXdevice', None)
			return redirect(url_for('config'))
	return render_template("config.html", page = page, form = form, text = text, selDMX = selDMX, changeDMX = changeDMX, menus = menu, foot = foot, url = url)

#---------- Авторизация ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
		return redirect(url_for('index'))
	ip = request.remote_addr
	page = 'Авторизация'
	data = 'login'
	text = ''
	lgn = formLogin()
	if request.method == "POST":
		login = lgn.login.data
		passwd = lgn.passwd.data
		if host.passwd('check', login, passwd):
			menu = host.admin_menu
			session['DMXlogin'] = 'admin'
			gv.log(f'[info] [web] User {ip} authentication success')
			return redirect(url_for('index'))
	gv.log(f'[error] [web] User {ip} authentication error')
	return render_template("admin.html", page = page, menus = menu, data=data, lgn=lgn, foot = foot, url = url)

#---------- Смена пароля и имени пользователя ----------
@app.route('/change_admin', methods=['GET', 'POST'])
def change_admin():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	page = 'Смена имени пользователя и пароля'
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
				gv.log(f'[warning] [web] User {ip} changed password')
		if ch_admin.login.data:
			login = ch_admin.login.data
			host.passwd('save', login, None)
			text = 'Имя пользователя успешно изменено'
			gv.log(f'[warning] [web] User {ip} changed login')
	return render_template("admin.html", page = page, menus = menu, text=text, data=data, ch_pass=ch_pass, ch_admin=ch_admin, foot = foot, url = url)

#---------- Logout ----------
@app.route('/logout')
def logout():
	ip = request.remote_addr
	session.pop('DMXlogin', None)
	gv.log(f'[info] [web] User {ip} logout success')
	return redirect(url_for('index'))

#---------- Настройка telegram ----------
@app.route('/telegram', methods=['GET', 'POST'])
def telegram():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	page = 'Настройка Telegram'
	token = formTokenTelegram()
	delToken = formDelTokenTelegram()
	addUser = formAddUserTelegram()
	delUser = formDelUserTelegram()
	delUser.name_user.choices = host.telegram('all_users')
	text = 'Сохраненный токен: ' + host.telegram('read_token')
	if request.method == "POST":
		if token.save_token.data:
			host.telegram('write_token', token.name_token.data)
			gv.log(f'[info] [web] User {ip} added new token for telegram')
			return redirect(url_for('telegram'))
		if addUser.save_user.data:
			host.telegram('add_user', addUser.name_id.data, addUser.name_user.data)
			gv.log(f'[info] [web] User {ip} added new user with ID {addUser.name_id.data} for telegram')
			return redirect(url_for('telegram'))
		if delUser.del_user.data:
			if delUser.name_user.data:
				host.telegram('del_user', delUser.name_user.data)
				gv.log(f'[warning] [web] User {ip} deleted user with ID {addUser.name_user.data} for telegram')
			return redirect(url_for('telegram'))
		if delToken.del_token.data:
			host.telegram('del_token')
			os.system('systemctl restart dmx-telegram')
			gv.log(f'[warning] [web] User {ip} deleted token for telegram')
			return redirect(url_for('telegram'))
	return render_template("telegram.html", page = page, text = text, menus = menu, token=token, delToken=delToken, addUser=addUser, delUser=delUser, foot = foot, url = url)
	
#---------- Update ----------
@app.route('/update', methods=['GET', 'POST'])
def update():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		page = 'Обслуживание'
		menu = host.admin_menu
	ip = request.remote_addr
	upd = formUpdate()
	text = ''
	error = host.error('read')
	f = 'false'
	if request.method == "POST":
		if upd.check_update.data:
			text = host.update('check')
			if 'update' in text:
				f = 'true'
			gv.log(f'[info] [web] User {ip} started check update system')
		if upd.update.data:
			host.update('update')
			gv.log(f'[warning] [web] User {ip} started upgrade system')
			return redirect(url_for('system', param = 'upgrade'))
		if upd.reboot.data:
			host.error('write', 'reboot', 'reboot')
			gv.log(f'[warning] [web] User {ip} started reboot system')
			return redirect(url_for('system', param = 'reboot'))
		if upd.reset.data:
			gv.restart()
			gv.log(f'[warning] [web] User {ip} started restart all services')
			return redirect(url_for('system', param = 'reset'))
	return render_template("update.html", page = page, menus = menu, text = text, upd = upd, f=f, error = error, foot = foot, url = url)
	
#---------- System ----------
@app.route('/system/<param>')
def system(param):
	if param == 'upgrade':
		page = ('Идет обновление системы...','Пожалуйста, Не предпринимайте никаких действий.','15000')
	elif param == 'reboot':
		page = ('Перезагрузка системы...','Пожалуйста, Не предпринимайте никаких действий.','60000')
	elif param == 'reset':
		page = ('Перезапуск всех служб...','Пожалуйста, Не предпринимайте никаких действий.','7000')
	elif 'backup' in param:
		file = param.split('`')[0]
		if gv.backup('restore', file):
			page = (f'Восстановление настроек из файла {file}...','Пожалуйста, Не предпринимайте никаких действий.','7000')
		else:
			page = (f'Файл {file} испорчен.',' Восстановление последней рабочей версии...','7000')
	else:
		abort(404)
	return render_template("system.html", page = page)

#---------- Setting ----------
@app.route('/setting', methods=['GET', 'POST'])
def setting():
	if not "DMXlogin" in session:
		menu = host.main_menu
		return redirect(url_for('login'))
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	page = 'Настройки'
	file = ''
	text = ''
	file_name = 'DMXbackup_' + time.strftime("%H-%M_%d-%m-%Y") + '.dmx'
	if gv.backup('create', file_name):
		file = file_name
	api = host.api('read')
	if request.method == "POST":
		if len(request.form) > 0:
			text = 'Файл резервной копии настроек не выбран'
			if request.form['api'] == 'on':
				host.api('enable')
				t = 'включен'
			elif request.form['api'] == 'off':
				host.api('disable')
				t = 'выключен'
			api = host.api('read')
			text = f'Доступ по API {t}.'
			gv.log(f"[info] [web] User {ip} changed setting api {request.form['api']}")
			return render_template("setting.html", page = page, menus = menu, host = host, text = text, file = file, api = api, foot = foot, url = url)
		backup = request.files['backup']
		bytes = int(request.headers.get('content-length'))
		if not backup:
			text = 'Файл резервной копии настроек не выбран'
			return render_template("setting.html", page = page, menus = menu, host = host, text = text, file = file, api = api, foot = foot, url = url)
		elif bytes >= 3000:
			text = 'Файл слишком большой для резервной копии настроек.'
			return render_template("setting.html", page = page, menus = menu, host = host, text = text, file = file, api = api, foot = foot, url = url)
		else:
			filename = secure_filename(backup.filename)
			if check_backup(filename):
				backup.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				gv.log(f'[warning] [web] User {ip} started recovery system from file {filename}')
				return redirect(url_for('system', param = filename+'`backup'))
			else:
				text = f'Файл {filename} не является резервной копией настроек.'
				return render_template("setting.html", page = page, menus = menu, host = host, text = text, file = file, api = api, foot = foot, url = url)
	return render_template("setting.html", page = page, menus = menu, host = host, text = text, file = file, api = api, foot = foot, url = url)
	
#---------- Download ----------
@app.route('/download/<path:files>', methods=['GET', 'POST'])
def download(files):
	ip = request.remote_addr
	path = gv.path + '/download/' + files
	log_file = gv.path + '/download/dmx_log.tar'
	if files == 'dmx_log.tar':
		gv.log(f'[info] [web] User {ip} downloaded logs file')
		gv.log('create', log_file)
		return send_file(log_file, as_attachment=True)
	if os.path.exists(path):
		gv.log(f'[info] [web] User {ip} downloaded backup file')
		return send_file(path, as_attachment=True)
	abort(404)

#---------- Error 404 ----------
@app.errorhandler(404)
def page_not_found(e):
	if not "DMXlogin" in session:
		menu = host.main_menu
	else:
		menu = host.admin_menu
	ip = request.remote_addr
	gv.log(f'[warning] [web] User {ip} request incorrect url')
	page = ''
	return render_template('404.html', page = page, menus = menu,  foot = foot, url = url), 404

#---------- API ----------
@app.route('/api/v1/dmx/<string:param>', methods=['GET'])
def api_info(param):
	ip = request.remote_addr
	if host.api('read').lower() == 'false':
		return jsonify({'Error':'API disabled'})
	errors = host.error('read')
	api = dict()
	api['status'] = dict()
	api['uuid'] = host.id_install()
	api['version'] = errors[0][1]
	api['debug'] = errors[1][1]
	api['mode'] = host.read_conf('default', 'mode')
	api['preset'] = host.read_conf('default', 'preset')
	api['dmxsender'] = host.read_conf('default', 'dmxsender')
	api['device'] = host.all_device()
	api['all_preset'] = ['default'] + host.get_preset()
	api['status']['sender_error'] = (errors[3][1]  if errors[3][1] else 'ok')
	api['status']['network_error'] = (errors[4][1]  if errors[4][1] else 'ok')
	api['status']['sys_error'] = (errors[5][1]  if errors[5][1] else 'ok')
	if param == 'all':
		gv.log(f'[info] [api] User {ip} requested all params')
		return jsonify(api)
	elif param in api:
		gv.log(f'[info] [api] User {ip} requested {param} params')
		return jsonify({param : api[param]})
	gv.log(f'[warning] [api] User {ip} requested incorrect {param} params')
	return jsonify({'Error':'Param '+str(param)+' not found'})

@app.route('/api/v1/dmx', methods=['POST'])
def api_control():
	ip = request.remote_addr
	if request.json:
		if host.api('read').lower() == 'false':
			return jsonify({'Error':'API disabled'})
		data = request.json
		reply = api_parse(data, ip)
	return jsonify(reply), 201

#---------- Temp Backdoor ----------
@app.route('/log')
def log():
	session['DMXlogin'] = 'admin'
	return redirect(url_for('index')) #'''

if __name__ == "__main__":
	app.run()
