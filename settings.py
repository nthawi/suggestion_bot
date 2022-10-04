import telebot
from telebot import types
import os
import configparser

global token
global config

config = configparser.RawConfigParser()
config.read('settings.ini')

print("Задайте настройки (можно пропустить клавишей enter)")

time_limit = input(f"Задайте время между отправками сообщений в секундах (0 - без ограничений). Сейчас {config['SETTINGS']['time_limit']}: ") 
if time_limit != "":
	config.set('SETTINGS', 'time_limit', str(time_limit))

reports_before_deletion = input(f"Задайте количество жалоб до удаления поста. Сейчас {config['SETTINGS']['reports_before_deletion']}: ")
if time_limit != "": 
	config.set('SETTINGS', 'reports_before_deletion', str(reports_before_deletion))

reports_before_ban = input(f"Задайте количество жалоб до бана. Сейчас {config['SETTINGS']['reports_before_ban']}: ") 
if time_limit != "":
	config.set('SETTINGS', 'reports_before_ban', str(reports_before_ban))

cfgfile = open('settings.ini','w')
config.write(cfgfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
cfgfile.close()

print("Настройки успешно обновлены! Для вступления в силу необходимо перезапустить бота либо отправить ему комманду /updatesettings")
