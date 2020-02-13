#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import error
import logging
import configparser
import sys
from datetime import datetime, time

def log_error(message):
	print(f"Error - {message}")
	logging.error(message)

def error_handler(update, context):
	try:
		raise context.error
	except error.Unauthorized:
		log_error("Unhandled Unauthorized exception.")
		# remove update.message.chat_id from conversation list
	except error.BadRequest:
		log_error("Unhandled BadRequest exception.")
		# handle malformed requests - read more below!
	except error.TimedOut:
		log_error("Unhandled TimedOut exception.")
		# handle slow connection problems
	except error.NetworkError:
		log_error("Unhandled NetworkError exception.")
		# handle other connection problems
	except error.ChatMigrated as e:
		log_error("Unhandled ChatMigrated exception.")
		# the chat_id of a group has changed, use e.new_chat_id instead
	except error.TelegramError:
		log_error("Unhandled TelegramError exception.")
		# handle all other telegram related errors

def main():

	#Logging-stuff
	logging.basicConfig(filename="InMemoriamBot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	logging.info("InMemoriamBot started.")

	# Create file for user list if not exist
	tmp_file = open('reminders.csv', 'a')
	tmp_file.close()

	# Get telegram API token and chat_id of bot owner from file ".bot_credentials"
	try:
		telegram_config = configparser.ConfigParser()
		telegram_config.read("./.bot_credentials")
		telegram_bot_token = telegram_config.get("configuration", "bot_token")
		telegram_bot_owner_chat_id = telegram_config.get("configuration", "bot_owner_chat_id")
		print(telegram_bot_token)
		print(telegram_bot_owner_chat_id)
	except configparser.NoSectionError as exception:
		log_error(exception)
		sys.exit(1)
	except configparser.NoOptionError as exception:
		log_error(exception)
		sys.exit(1)

	try:
		InMemoriamBotUpdater = Updater(token=telegram_bot_token, use_context=True)
		InMemoriamBotDispatcher = InMemoriamBotUpdater.dispatcher
		InMemoriamBot = InMemoriamBotUpdater.bot
	except telegram.error.InvalidToken as exception:
		log_error("Invalid bot API token.")
		sys.exit(1)

	# Notify bot owner that bot has started
	InMemoriamBot.send_message(chat_id=telegram_bot_owner_chat_id, text="InMemoriamBot was started at " + datetime.now().strftime('%d.%m.%y (%a) at %H:%M:%S'))
	

if __name__ == '__main__':
	main()
