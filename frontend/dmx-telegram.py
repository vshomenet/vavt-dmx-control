#!/usr/bin/python3
import re
import json
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from classConfig import *

gv = GlobalVar()
host = ConfigHost(gv.path)
token = host.telegram('read_token')
gv.create_conf()

if not token or re.match(r'^\d+:[a-zA-Z\d]+$', token) is None:
	token = '1:q'
	
bot = Bot(token)
dp = Dispatcher(bot)

list_id = host.telegram('all_users')

text_help = '\nВы находитесь в раделе помощь. \
			\nСписок доступных команд: \
			\n/start вызов главного меню \
			\n/preset вызов меню загрузки \
			\n/help вызов меню справки \
			\n/id показать мой ID \
			\n/status показать состояние системы'

text_preset = '\nВы находитесь в разделе управление. \
				\nКакой пресет вы хотите загрузить? \
				\nСейчас активен пресет: '
				 
text_menu = '\nВы находитесь в главном меню бота'

text_error_id = '\nУ Вас нет доступа к разделу управления. \
				\nПожалуйста обратитесь к администратору сервера и сообщите ему свой ID. \
				\nЕсли вы являетесь администратором, тогда перейдите в вебинтерфейс сервера \
				и добавьте свой ID в список разрешенных. \
				\nИнструкцию по добавлению можно найти на сайте проекта.\
				\nВаш ID:\n'

text_status = '\nВы находитесь в разделе состояние системы.'

# Чтение ошибок
def error():
	text = ''
	errors = host.error('read')
	text = text + '\nЗагружен пресет: ' + host.activate_preset('read')
	text = text + '\nВерсия программного обеспечения: ' + errors[0][1]
	text = text + '\nРежим отладки: ' + errors[1][1]
	text = text + '\nКонтроллер управления: ' + (errors[3][1]  if errors[3][1] else 'ok')
	text = text + '\nСистема: ' + (errors[5][1]  if errors[5][1] else 'ok')
	return text

# Главное меню
def menu_main():
	keyboard = InlineKeyboardMarkup(row_width=2)
	btn_menu = (('Главное меню', 'start'), ('Управление', 'preset'), ('Состояние системы', 'status'), ('Помощь', 'help'))
	list_button = (InlineKeyboardButton(text, callback_data=data) for text, data in btn_menu)
	keyboard.add(*list_button)
	return keyboard
	
# Меню preset
def menu_preset(param):
	preset = ['default']
	if param == 'preset':
		preset += host.get_preset()
		return preset
	if param == 'menu':
		keyboard = InlineKeyboardMarkup(row_width=2)
		buttons = list()
		presets = preset + host.get_preset()
		for pres in presets:
			buttons.append((pres, pres))
		list_button = (InlineKeyboardButton(text, callback_data=data) for text, data in buttons)
		keyboard.add(*list_button)
		keyboard.add(InlineKeyboardButton(text = 'Главное меню', callback_data = 'start'))
		return keyboard

# Меню help
def menu_help():
	keyboard = InlineKeyboardMarkup(row_width=2)
	btn_menu = (('Главное меню', 'start'), ('Управление','preset'), ('Состояние системы', 'status'))
	list_button = (InlineKeyboardButton(text, callback_data=data) for text, data in btn_menu)
	keyboard.add(*list_button)
	keyboard.add(InlineKeyboardButton('Сайт проекта', url='https://github.com/vshomenet/vavt-dmx-control'))
	return keyboard
	
# Ответ на команду start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	text = 'Добрый день '
	text += message.from_user.full_name
	text += text_menu
	await bot.send_message(message.from_user.id, text, reply_markup = menu_main())
	
# Ответ на команду preset
@dp.message_handler(commands='preset')
async def start_cmd_handler(message: types.Message):
	if str(message.from_user.id) in list_id:
		text = message.from_user.full_name + text_preset  +  host.activate_preset('read')
		await bot.send_message(message.from_user.id, text, reply_markup = menu_preset('menu'))
	else:
		text = message.from_user.full_name + text_error_id + str(message.from_user.id)
		await bot.send_message(message.from_user.id, text , reply_markup = menu_help())
	
# Ответ на команду id
@dp.message_handler(commands=['id'])
async def process_start_command(message: types.Message):
	text = message.from_user.full_name + '\nВаш ID:\n' + str(message.from_user.id)
	await bot.send_message(message.from_user.id, text , reply_markup = menu_main())

# Ответ на команду help
@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
	text = message.from_user.full_name + text_help
	await bot.send_message(message.from_user.id, text, reply_markup = menu_help())

# Ответ на команду status
@dp.message_handler(commands=['status'])
async def process_start_command(message: types.Message):
	text = message.from_user.full_name + text_status + error()
	await bot.send_message(message.from_user.id, text, reply_markup = menu_main())
	
# Ответ на произвольный текст
@dp.message_handler()
async def echo_message(message: types.Message):
	if message.text in menu_preset('preset') and str(message.from_user.id) in list_id:
		text = message.from_user.full_name + f'\nПресет {message.text} успешно загружен'
		host.activate_preset('write', message.text)
	else:
		text = message.from_user.full_name + f'\nНеизвестная команда "{message.text}"'
	await bot.send_message(message.from_user.id, text, reply_markup = menu_main())
	
# Обработка кнопок меню
@dp.callback_query_handler(text=menu_preset('preset') + ['start', 'preset', 'help', 'status'])
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
	if query.data in menu_preset('preset') and str(query.from_user.id) in list_id:
		await query.answer(f'Загружаем пресет {query.data}')
		host.activate_preset('write', query.data)
		text = query.from_user.full_name + f'\nПресет {query.data} успешно загружен'
		await bot.send_message(query.from_user.id, text, reply_markup = menu_preset('menu'))
	elif query.data == 'start':
		await query.answer(f'Переходим в главное меню')
		text = query.from_user.full_name + text_menu
		await bot.send_message(query.from_user.id, text, reply_markup = menu_main())
	elif query.data == 'preset' and str(query.from_user.id) in list_id :
		await query.answer(f'Переходим в раздел управления')
		text = query.from_user.full_name + text_preset +  host.activate_preset('read')
		await bot.send_message(query.from_user.id, text, reply_markup = menu_preset('menu'))
	elif query.data == 'help':
		await query.answer(f'Переходим в раздел помощь')
		text = query.from_user.full_name + text_help
		await bot.send_message(query.from_user.id, text, reply_markup = menu_help())
	elif query.data == 'status':
		await query.answer(f'Переходим в раздел состояние системы')
		text = query.from_user.full_name + text_status + error()
		await bot.send_message(query.from_user.id, text, reply_markup = menu_main())
	else:
		text = query.from_user.full_name + text_error_id + str(query.from_user.id)
		await bot.send_message(query.from_user.id, text , reply_markup = menu_help())

# Старт программы
if __name__ == '__main__':
	try:
		executor.start_polling(dp)
	except Exception as e:
		sys.exit(1)
