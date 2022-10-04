import telebot
import sqlite3
from telebot import types
import os
import configparser
import time

global token
global config

config = configparser.RawConfigParser()
config.read('settings.ini')

print('Доброго времени суток, Вас приветствует мастер установки и базовой настройки Вашего нового бота')
print('Для начала необходимо создать бота, для этого:')
print('1) в телеграме находим бота @botfather')
print('2) нажимаем /start,  вводим /newbot')
print('3) придумываем имя бота и отправляем')
print('4) придумываем юзернейм бота (имя должно оканчиваться на "bot")')
print('После создания необходимо нажать на синюю строчку с токеном (формата цифры:буквы) чтобы скопировать токен. Более детальную инструкцию можно найти в интернете')
print('~Если бот у Вас уже есть, Вы можете вставить его токен ниже')
token = input('После этого вставьте сюда токен нажав правую кнопку мыши и нажмите enter: ')
token = token.strip() 

bot = telebot.TeleBot(token)

print('Бот будет запущен, дальнейшая установка будет продолжена в самом боте. Для продолжения введите в боте /start')

@bot.message_handler(commands=['start'])
def start(message):

	global token
	global config	

	bot.send_message(message.chat.id, f'Отлично! Теперь добавь меня в канал и перешли мне любое сообщение из этого канала')

	# Бот запущен. Записываем токен как верный
	config.set('BOTSETTINGS', 'token', str(token))

@bot.message_handler(content_types = ['text','video','sticker', 'video_note', 'location', 'audio', 'document'])
def echo_all(message):

	global config 

	try:
		forwarded_from = message.forward_from_chat.id
	except AttributeError:

		bot.send_message(message.chat.id, f'Необходимо переслать мне сообщение из канала или от лица канала')
		return

	message_to_send = f'Текущий айди канала {message.forward_from_chat.id} ({message.forward_from_chat.title}) был записан как основной \n'
	message_to_send = message_to_send + 'Вы как пользователь установлены в качестве владельца бота\n\n'
	message_to_send = message_to_send + 'Первичная настройка завершена! Для продолжения работы со стандартными настройками более ничего не требуется\n\n'
	message_to_send = message_to_send + 'Настройки может редактировать только создатель. Для запуска бота воспользуйтесь ярлыком start.bat. Если есть необходимость изменить настройки, необходимо набрать комманду /settings. Приятного пользования!\n\n'
	message_to_send = message_to_send + 'Работа бота в текущем процессе будет остановлена'

	bot.send_message(message.chat.id, message_to_send)

	config.set('BOTSETTINGS', 'channel_id', str(message.forward_from_chat.id))
	config.set('BOTSETTINGS', 'owner', str(message.from_user.username))

	cfgfile = open('settings.ini','w')
	config.write(cfgfile, space_around_delimiters=False)
	cfgfile.close()

	connect = sqlite3.connect('db/posts.db')
	cursor = connect.cursor()

	cursor.execute('''CREATE TABLE IF NOT EXISTS posts_data(
			post_id INTEGER,
			user_id INTEGER,
			upvote BOOLEAN,
			reportvote BOOLEAN
		)''')

	connect.commit()

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

		time_ok = time.time() - 10000
		user_info = [message.chat.id, message.chat.username, False, 0, 0, 0, time_ok]
		cursor.execute("INSERT INTO user_data VALUES(?,?,?,?,?,?,?);", user_info)
		connect.commit()

	pid = str(os.getpid())
	os.system(f'taskkill /pid {pid} /F')
	quit()	

bot.polling()

print('Ошибка запуска бота, неверный токен. Проверьте точность введенных данных и попробуйте снова')

time.sleep(5)