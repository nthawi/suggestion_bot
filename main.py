import sqlite3
import telebot
import time
from telebot import types
import re
import configparser

global owner
global current_chat_id
global time_limit
global reports_before_deletion
global reports_before_ban
global enable_unsupported_types
global enable_signature
global enable_buttons
global start_message

# Конфиг
config = configparser.ConfigParser()
config.read('settings.ini', 'CP1251')
config.sections()

token = 					config['BOTSETTINGS']['token']
current_chat_id = 			config['BOTSETTINGS']['channel_id']
owner = 					str(config['BOTSETTINGS']['owner'])
time_limit = 				int(config['SETTINGS']['time_limit'])
reports_before_deletion = 	int(config['SETTINGS']['reports_before_deletion'])
reports_before_ban = 		int(config['SETTINGS']['reports_before_ban'])
enable_unsupported_types = 	bool(config.getboolean('SETTINGS', 'enable_unsupported_types'))
enable_signature = 			bool(config.getboolean('SETTINGS', 'enable_signature'))
enable_buttons = 			bool(config.getboolean('SETTINGS', 'enable_buttons'))
start_message = 			str(config['SETTINGS']['start_message'])

bot = telebot.TeleBot(token)

if token == '' or current_chat_id == '' or owner == '':

	print('Для начала необходимо настроить бота. Для этого запустите "start setup" и следуйте инструкциям')

	time.sleep(5)
	quit()

@bot.message_handler(commands=['start'])
def start(message):

	global time_limit
	global start_message

	if chat_type_is_ignore(message):
		return

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS user_data(
			id INTEGER,
			username VARCHAR(255),
			banned BOOLEAN,
			reports INTEGER,
			points INTEGER,
			rank INTEGER,
			lastmessage DATE
		)""")

	connect.commit()

	current_id = message.chat.id
	cursor.execute(f"SELECT * FROM user_data WHERE id = {current_id}")
	data = cursor.fetchone()

	if data is None:

		time_ok = time.time() - time_limit
		user_info = [message.chat.id, message.chat.username, False, 0, 0, 0, time_ok]
		cursor.execute("INSERT INTO user_data VALUES(?,?,?,?,?,?,?);", user_info)
		connect.commit()

		bot.send_message(message.chat.id, start_message, parse_mode='Markdown')

	else:

		if user_banned(message.from_user.id):
			return

		bot.send_message(message.chat.id, "Для поиска необходимой информации воспользуйтесь коммандой /help")

@bot.message_handler(commands=['updatesettings'])
def start(message):

	if chat_type_is_ignore(message):
		return

	global time_limit
	global reports_before_deletion
	global reports_before_ban
	global enable_unsupported_types
	global enable_signature
	global enable_buttons

	config = configparser.ConfigParser()
	config.read('settings.ini', 'CP1251')
	config.sections()

	time_limit = 				int(config['SETTINGS']['time_limit'])
	reports_before_deletion = 	int(config['SETTINGS']['reports_before_deletion'])
	reports_before_ban = 		int(config['SETTINGS']['reports_before_ban'])
	enable_unsupported_types = 	bool(config.getboolean('SETTINGS', 'enable_unsupported_types'))
	enable_signature = 			bool(config.getboolean('SETTINGS', 'enable_signature'))
	enable_buttons = 			bool(config.getboolean('SETTINGS', 'enable_buttons'))

	bot.send_message(message.chat.id, "Настройки бота были успешно обновлены!")	

@bot.message_handler(commands=['settings'])
def start(message):

	if chat_type_is_ignore(message):
		return

	global time_limit
	global reports_before_deletion
	global reports_before_ban
	global enable_unsupported_types
	global enable_signature
	global start_message
	global enable_buttons

	if enable_unsupported_types == True:
		enable_unsupported_types_ru = "Да"
	else:
		enable_unsupported_types_ru = "Нет"

	if enable_signature == True:
		enable_signature_ru = "Да"
	else:
		enable_signature_ru = "Нет"

	if enable_buttons == True:
		enable_buttons_ru = "Да"
	else:
		enable_buttons_ru = "Нет"

	message_current_settings = "Текущие настройки:\n\n"
	message_current_settings = message_current_settings + f"Время между сообщениями (сек): *{time_limit}*\n"
	message_current_settings = message_current_settings + f"Репортов до удаления: *{reports_before_deletion}*\n"
	message_current_settings = message_current_settings + f"Репортов до бана: *{reports_before_ban}*\n"
	message_current_settings = message_current_settings + f"Разрешить неподдерживаемые форматы (геолокация, стикеры, видеокруги): *{enable_unsupported_types_ru}*\n"
	message_current_settings = message_current_settings + f"Публиковать с подписью: *{enable_signature_ru}*\n"
	message_current_settings = message_current_settings + f"Отображать кнопки: *{enable_buttons_ru}*\n"
	message_current_settings = message_current_settings + f"Приветственное сообщение: *{start_message}*\n"

	bot.send_message(message.chat.id, message_current_settings, parse_mode='Markdown', reply_markup=get_settings_button())	

@bot.message_handler(commands=['score'])
def test(message):

	if user_banned(message.from_user.id):
		return

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	current_id = message.from_user.id

	cursor.execute(f"SELECT points FROM user_data WHERE id = {current_id}")
	data = cursor.fetchone()

	if data is None:
		bot.send_message(message.chat.id, "У вас еще нет заработанных очков")
	else:
		bot.send_message(message.chat.id, f"Ваш счет: {data[0]}")

@bot.message_handler(commands=['ban'])
def test(message):

	username = message.text.replace('/ban', '') 
	username = username.replace('@', '') 
	username = username.replace(' ', '') 

	if username == "": 
		bot.send_message(message.chat.id, "Необходимо указать юзернейм пользователя")
		return

	current_id = message.text

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	try:
		cursor.execute("UPDATE user_data SET banned = 1 WHERE username = ?", (str(username),))
	except Exception as e:
		print(repr(e))

	connect.commit()

	bot.send_message(message.chat.id, f"Пользователь @{username} забанен")

@bot.message_handler(commands=['unban'])
def test(message):

	username = message.text.replace('/unban', '') 
	username = username.replace('@', '') 
	username = username.replace(' ', '') 

	if username == "": 
		bot.send_message(message.chat.id, "Необходимо указать юзернейм пользователя")
		return

	current_id = message.text

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	try:
		cursor.execute("UPDATE user_data SET banned = 0, reports = 0 WHERE username = ?", (str(username),))
	except Exception as e:
		print(repr(e))

	connect.commit()

	bot.send_message(message.chat.id, f"Пользователь @{username} разбанен")

@bot.message_handler(content_types = ["sticker", "video_note", "location"])
def photo(message):

	global enable_unsupported_types
	global current_chat_id
	global enable_signature

	if chat_type_is_ignore(message):
		return

	if not enable_unsupported_types:
		bot.send_message(message.chat.id, f"Данный тип контента не поддерживается")
		return	

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	message_text = f"{message.text}\nПоделился @{message.from_user.username}"

	message_id = bot.forward_message(current_chat_id, message.chat.id, message.message_id)

	update_message_time(message, message_id)

@bot.message_handler(content_types = ["video"])
def photo(message):

	global current_chat_id
	global enable_signature

	if chat_type_is_ignore(message):
		return

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	post_id = message.message_id
	user_id = message.from_user.id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	if message.caption == None:
		caption = f"Поделился @{message.from_user.username} ({message.from_user.id})"
	else:
		caption = f"{message.caption}\nПоделился @{message.from_user.username} ({message.from_user.id})"

	if not enable_signature:
		caption = message.caption

	message_id = bot.send_video(current_chat_id, message.video.file_id, caption=caption, reply_markup=get_like_button())

	update_message_time(message, message_id)

@bot.message_handler(content_types = ["audio"])
def photo(message):

	global current_chat_id
	global enable_signature

	if chat_type_is_ignore(message):
		return

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	post_id = message.message_id
	user_id = message.from_user.id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	if message.caption == None:
		caption = f"Поделился @{message.from_user.username} ({message.from_user.id})"
	else:
		caption = f"{message.caption}\nПоделился @{message.from_user.username} ({message.from_user.id})"

	if not enable_signature:
		caption = message.caption	

	message_id = bot.send_audio(current_chat_id, message.audio.file_id, caption=caption, reply_markup=get_like_button())

	update_message_time(message, message_id)

@bot.message_handler(content_types = ["document"])
def photo(message):

	global current_chat_id
	global enable_signature

	if chat_type_is_ignore(message):
		return

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	post_id = message.message_id
	user_id = message.from_user.id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	if message.caption == None:
		caption = f"Поделился @{message.from_user.username} ({message.from_user.id})"
	else:
		caption = f"{message.caption}\nПоделился @{message.from_user.username} ({message.from_user.id})"

	if not enable_signature:
		caption = message.caption	

	message_id = bot.send_document(current_chat_id, message.document.file_id, caption=caption, reply_markup=get_like_button())

	update_message_time(message, message_id)

@bot.message_handler(content_types = ["photo"])
def photo(message):

	global current_chat_id
	global enable_signature

	if chat_type_is_ignore(message):
		return

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	post_id = message.message_id
	user_id = message.from_user.id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	if message.caption == None:
		caption = f"Поделился @{message.from_user.username} ({message.from_user.id})"
	else:
		caption = f"{message.caption}\nПоделился @{message.from_user.username} ({message.from_user.id})"

	if not enable_signature:
		caption = message.caption

	message_id = bot.send_photo(current_chat_id, message.photo[-1].file_id, caption=caption, reply_markup=get_like_button())

	update_message_time(message, message_id)

@bot.message_handler(content_types = "text")
def echo_all(message):

	if chat_type_is_ignore(message):
		return

	global current_chat_id
	global owner
	global enable_signature

	if owner == message.from_user.username:
		if change_settings(message):
			return

	if user_banned(message.from_user.id):
		return

	time_before_send = overheat_timer(message)

	if time_before_send > 0:
		bot.send_message(message.chat.id, f"Перед отправкой необходимо подождать еще {round(time_before_send)} секунд")
		return

	if enable_signature:
		message_text = f"{message.text}\nПоделился @{message.from_user.username} ({message.from_user.id})"
	else:
		message_text = f"{message.text}"

	message_id = bot.send_message(current_chat_id, text=message_text, reply_markup=get_like_button())

	update_message_time(message, message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	try:
		if call.message:
			if call.data == 'like':
				apply_like(call)
			if call.data == 'report':
				apply_report(call)
					
	except Exception as e:
		print(repr(e))

def update_message_time(message, message_id):

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	current_id = message.chat.id
	current_date = time.time()
	cursor.execute(f"UPDATE user_data SET lastmessage = {current_date} WHERE id = {current_id}")

	connect.commit()

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	user_info = [message_id.message_id, current_id, False, False]
	cursor.execute("INSERT INTO posts_data VALUES(?,?,?,?);", user_info)

	connect.commit()

def overheat_timer(message):

	global time_limit

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	current_id = message.chat.id
	cursor.execute(f"SELECT lastmessage FROM user_data WHERE id = {current_id}")
	data = cursor.fetchone()

	if (time.time() - data[0]) < time_limit:
		return time_limit - (time.time() - data[0])
	else:
		return 0

def user_banned(user_id, message_id=None):

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS user_data(
			id INTEGER,
			username VARCHAR(255),
			banned BOOLEAN,
			reports INTEGER,
			points INTEGER,
			rank INTEGER,
			lastmessage DATE
		)""")

	connect.commit()

	cursor.execute(f"SELECT banned FROM user_data WHERE id = {user_id}")
	data = cursor.fetchone()
	
	if data is None:
		if message_id != None:
			bot.answer_callback_query(callback_query_id=message_id, show_alert=False, text="Сначала необходимо авторизоваться в боте!")

		return False

	if data[0] == 1:
		#bot.send_message(message.chat.id, "Забанен лалка")
		return True
	else:
		return False

def apply_like(message):

	post_id = message.message.message_id
	user_id = message.from_user.id

	if user_banned(user_id, message.id):
		return

	if like_exist(user_id, post_id):
		bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Отметка 'нравится' уже поставлена!")
		return

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	cursor.execute(f"SELECT * FROM posts_data WHERE post_id = {post_id} AND user_id = {user_id}")
	data = cursor.fetchone()

	if data is None:

		# Создание записи о посте
		try:

			user_info = [post_id, user_id, True, False]
			cursor.execute("INSERT INTO posts_data VALUES(?,?,?,?);", user_info)
			connect.commit()

			bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Ваш голос учтен!")

		except Exception as e:
			print(repr(e))

		add_point(message.message)

	else:

		try:
			cursor.execute(f"UPDATE posts_data SET upvote=TRUE WHERE post_id = {post_id} AND user_id = {user_id}")
			connect.commit()

			bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Ваш голос учтен!")
		
		except Exception as e:
			print(repr(e))

		add_point(message.message)

	try:

		cursor.execute(f"SELECT COUNT(1) FROM posts_data WHERE post_id = {post_id} AND upvote=TRUE")
		data = cursor.fetchone()

	except Exception as e:
		print(repr(e))

	if data is None or data[0] == 0:

		markup = types.InlineKeyboardMarkup()
		item1 = types.InlineKeyboardButton(text="Нравится", callback_data='like')
		item2 = types.InlineKeyboardButton(text="Жалоба", callback_data='report')

		markup.add(item1, item2)

		bot.edit_message_reply_markup(chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=markup)

	else:

		markup = types.InlineKeyboardMarkup()

		button_text = f"Нравится ({data[0]})"
		item1 = types.InlineKeyboardButton(text=button_text, callback_data='like')
		item2 = types.InlineKeyboardButton(text="Жалоба", callback_data='report')

		markup.add(item1, item2)

		bot.edit_message_reply_markup(chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=markup)

def add_point(message):

	post_id = message.message_id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute(f"SELECT user_id FROM posts_data WHERE post_id = {post_id}")
	data = cursor.fetchone()

	user_id = data[0]

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	cursor.execute(f"UPDATE user_data SET points = points+1 WHERE id = {user_id}")

	connect.commit()

def like_exist(user_id, post_id):

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute(f"SELECT user_id FROM posts_data WHERE post_id = {post_id} AND user_id = {user_id} AND upvote=TRUE")
	data = cursor.fetchone()

	if data is None:
		return False
	else:
		return True

def apply_report(message):

	post_id = message.message.message_id
	user_id = message.from_user.id

	if user_banned(user_id, message.id):
		return

	if report_exist(user_id, post_id):
		bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Жалоба уже отправлена!")
		return

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)""")

	connect.commit()

	cursor.execute(f"SELECT * FROM posts_data WHERE post_id = {post_id} AND user_id = {user_id}")
	data = cursor.fetchone()

	if data is None:

		# Создание записи о посте
		try:

			user_info = [post_id, user_id, False, True]
			cursor.execute("INSERT INTO posts_data VALUES(?,?,?,?);", user_info)
			connect.commit()
			bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Жалоба отправлена!")

		except Exception as e:
			print(repr(e))

		add_report(message.message)

	else:

		try:
			cursor.execute(f"UPDATE posts_data SET reportvote=TRUE WHERE post_id = {post_id} AND user_id = {user_id}")
			connect.commit()
			bot.answer_callback_query(callback_query_id=message.id, show_alert=False, text="Жалоба отправлена!")
		
		except Exception as e:
			print(repr(e))

		add_report(message.message)

def report_exist(user_id, post_id):

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute(f"SELECT user_id FROM posts_data WHERE post_id = {post_id} AND user_id = {user_id} AND reportvote=TRUE")
	data = cursor.fetchone()

	if data is None:
		return False
	else:
		return True

def add_report(message):

	global reports_before_deletion
	global reports_before_ban
	global current_chat_id

	post_id = message.message_id

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute(f"SELECT user_id FROM posts_data WHERE post_id = {post_id}")
	data = cursor.fetchone()

	user_id = data[0]

	cursor.execute(f"SELECT COUNT(1) FROM posts_data WHERE post_id = {post_id} AND reportvote = 1")
	data = cursor.fetchone()

	if (data[0] + 1) > reports_before_deletion:
		bot.delete_message(chat_id=current_chat_id, message_id=message.message_id);

	connect = sqlite3.connect('db/users.db')
	cursor = connect.cursor()

	cursor.execute(f"SELECT reports FROM user_data WHERE id = {user_id}")
	data = cursor.fetchone()

	# сегодня без бана впредь будьте аккуратнее
	if reports_before_ban == 0:
		cursor.execute(f"UPDATE user_data SET reports = reports+1 WHERE id = {user_id}")
	else:

		if (data[0] + 1) < reports_before_ban:
			cursor.execute(f"UPDATE user_data SET reports = reports+1 WHERE id = {user_id}")
		else:
			cursor.execute(f"UPDATE user_data SET banned = TRUE WHERE id = {user_id}")

	connect.commit()

def chat_type_is_ignore(message):

	if message.chat.type == 'group' or message.chat.type == 'supergroup' or message.chat.type == 'channel':
		return True
	else:
		return False

def change_settings(message):

	global owner
	global current_chat_id
	global time_limit
	global reports_before_deletion
	global reports_before_ban
	global enable_unsupported_types
	global enable_signature
	global start_message
	global enable_buttons

	# обработка кнопок
	if message.text == 'Между сообщениями':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Время в секундах:', reply_markup=markup)

		return True

	if message.text == 'До удаления':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Количество дизлайков до удаления поста:', reply_markup=markup)
		return True

	if message.text == 'До бана':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Количество дизлайков до бана пользователя (0 - бан отключен):', reply_markup=markup)
		return True

	if message.text == 'Неподдерживаемые форматы':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Включить неподдерживаемые форматы:', reply_markup=markup)
		return True

	if message.text == 'Подпись':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Включить подписи:', reply_markup=markup)
		return True

	if message.text == 'Кнопки':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Отображать кнопки:', reply_markup=markup)
		return True

	if message.text == 'Приветственное сообщение':

		markup = types.ForceReply(selective=False)
		bot.send_message(message.chat.id, 'Введите приветственное сообщение:', reply_markup=markup)
		return True

	if message.text == 'Сохранить':

		bot.send_message(message.chat.id, 'Настройки бота были успешно обновлены!', reply_markup=types.ReplyKeyboardRemove())
		return True
	
	# обработка настроек
	if message.reply_to_message is not None:

		if message.reply_to_message.text == 'Время в секундах:':

			try:
				time_limit = int(message.text)
				save_settings()
				bot.send_message(message.chat.id, f'Время между сообщениями изменено на {message.text}. Настройки сохранены', reply_markup=get_settings_button())
				return True

			except Exception as e:
				bot.send_message(message.chat.id, 'Необходимо указать время числом!', reply_markup=get_settings_button())
				return True

		if message.reply_to_message.text == 'Количество дизлайков до удаления поста:':

			try:
				reports_before_deletion = int(message.text)
				save_settings()
				bot.send_message(message.chat.id, f'Количество дизлайков до удаления изменено на {message.text}. Настройки сохранены', reply_markup=get_settings_button())
				return True

			except Exception as e:
				bot.send_message(message.chat.id, 'Необходимо указать количество числом!', reply_markup=get_settings_button())
				return True

		if message.reply_to_message.text == 'Количество дизлайков до бана пользователя (0 - бан отключен):':

			try:
				reports_before_ban = int(message.text)
				save_settings()
				bot.send_message(message.chat.id, f'Количество дизлайков до бана изменено на {message.text}. Настройки сохранены', reply_markup=get_settings_button())
				return True

			except Exception as e:
				bot.send_message(message.chat.id, 'Необходимо указать количество числом!', reply_markup=get_settings_button())
				return True

		if message.reply_to_message.text == 'Включить неподдерживаемые форматы:':

			if message.text.lower() == 'да' or message.text.lower() == 'д' or message.text.lower() == 'y' or message.text == '1':
				enable_unsupported_types = True
				save_settings()	
				bot.send_message(message.chat.id, 'Неподдерживаемые форматы включены. Настройки сохранены', reply_markup=get_settings_button())
				return True

			if message.text.lower() == 'нет' or message.text.lower() == 'н' or message.text.lower() == 'n' or message.text == '0':
				enable_unsupported_types = False
				save_settings()	
				bot.send_message(message.chat.id, 'Неподдерживаемые форматы выключены. Настройки сохранены', reply_markup=get_settings_button())
				return True

			bot.send_message(message.chat.id, 'Необходимо ввести "да", "д", "y", "1" для включения или "нет", "н", "n", "0" для выключения', reply_markup=get_settings_button())
			return True

		if message.reply_to_message.text == 'Включить подписи:':

			if message.text.lower() == 'да' or message.text.lower() == 'д' or message.text.lower() == 'y' or message.text == '1':
				enable_signature = True
				save_settings()	
				bot.send_message(message.chat.id, 'Подписи включены. Настройки сохранены', reply_markup=get_settings_button())
				return True

			if message.text.lower() == 'нет' or message.text.lower() == 'н' or message.text.lower() == 'n' or message.text == '0':
				enable_signature = False
				save_settings()	
				bot.send_message(message.chat.id, 'Подписи выключены. Настройки сохранены', reply_markup=get_settings_button())
				return True

			bot.send_message(message.chat.id, 'Необходимо ввести "да", "д", "y", "1" для включения или "нет", "н", "n", "0" для выключения', reply_markup=get_settings_button())
			return True

		if message.reply_to_message.text == 'Отображать кнопки:':

			if message.text.lower() == 'да' or message.text.lower() == 'д' or message.text.lower() == 'y' or message.text == '1':
				enable_buttons = True
				save_settings()	
				bot.send_message(message.chat.id, 'Отображение кнопок включено. Настройки сохранены', reply_markup=get_settings_button())
				return True

			if message.text.lower() == 'нет' or message.text.lower() == 'н' or message.text.lower() == 'n' or message.text == '0':
				enable_buttons = False
				save_settings()	
				bot.send_message(message.chat.id, 'Отображение кнопок выключено. Настройки сохранены', reply_markup=get_settings_button())
				return True

			bot.send_message(message.chat.id, 'Необходимо ввести "да", "д", "y", "1" для включения или "нет", "н", "n", "0" для выключения', reply_markup=get_settings_button())
			return True

		if message.reply_to_message.text == 'Введите приветственное сообщение:':

			start_message = message.text
			save_settings()
			bot.send_message(message.chat.id, f'Приветственное сообщение изменено на:\n\n {message.text}\n\n Настройки сохранены', parse_mode='Markdown', reply_markup=get_settings_button())
			return True

	return False

def get_settings_button():

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Между сообщениями')
	item2 = types.KeyboardButton('До удаления')
	item3 = types.KeyboardButton('До бана')
	item4 = types.KeyboardButton('Неподдерживаемые форматы')
	item5 = types.KeyboardButton('Подпись')
	item6 = types.KeyboardButton('Кнопки')
	item7 = types.KeyboardButton('Приветственное сообщение')
	item8 = types.KeyboardButton('Сохранить')

	markup.add(item1, item2)
	markup.add(item3, item4)
	markup.add(item5, item6)
	markup.add(item7, item8)

	return markup	

def get_like_button():

	global enable_buttons

	if not enable_buttons:
		return None

	markup = types.InlineKeyboardMarkup()
	item1 = types.InlineKeyboardButton(text="Нравится", callback_data='like')
	item2 = types.InlineKeyboardButton(text="Жалоба", callback_data='report')

	markup.add(item1, item2)

	return markup

def get_yesno_button():

	#markup = types.ForceReply(selective=False)
	markup = types.ReplyKeyboardRemove(resize_keyboard=True)
	item1 = types.KeyboardButton('Да')
	item2 = types.KeyboardButton('Нет')

	markup.add(item1, item2)

	return markup	

def save_settings():

	global owner
	global current_chat_id
	global time_limit
	global reports_before_deletion
	global reports_before_ban
	global enable_unsupported_types
	global enable_signature
	global start_message
	global enable_buttons

	config.set('SETTINGS', 'time_limit', str(time_limit))
	config.set('SETTINGS', 'reports_before_deletion', str(reports_before_deletion))
	config.set('SETTINGS', 'reports_before_ban', str(reports_before_ban))
	config.set('SETTINGS', 'enable_unsupported_types', str(enable_unsupported_types))
	config.set('SETTINGS', 'enable_signature', str(enable_signature))
	config.set('SETTINGS', 'enable_buttons', str(enable_buttons))
	config.set('SETTINGS', 'start_message', str(start_message))

	cfgfile = open('settings.ini', 'w')
	config.write(cfgfile, space_around_delimiters=False)
	cfgfile.close()

bot.infinity_polling()