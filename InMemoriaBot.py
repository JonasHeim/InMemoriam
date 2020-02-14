#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import error
import logging
import configparser
import sys
from datetime import datetime, time, timezone, timedelta
import csv
import shutil

def get_timezone():
	return timezone(timedelta(1))

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

def load_reminder_list():
	reminders = []
	try:
		#CSV shall be opened with newline=''
		#https://docs.python.org/3.8/library/csv.html#csv.reader
		with open('reminders.csv', 'r', newline='') as file:
			reader = csv.reader(file, delimiter=',')
			for row in reader:
				reminders.append(row)
	except Exception as exception:
		log_error(exception)
	finally:
		return reminders

def send_reminder(context: telegram.ext.CallbackContext, message):
	logging.info("Sending reminder \"%s\"", message)
	reminder_message = f"Reminder #{context.job.context['reminder_id']}\r\n{message}\r\n\r\n/dismiss {context.job.context['reminder_id']}"
	context.bot.send_message(chat_id=context.job.context['chat_id'], text=reminder_message)

def check_reminder_list(context: telegram.ext.CallbackContext):
	reminder_list = load_reminder_list()
	if reminder_list:
		#Get current time
		current_time = datetime.strptime(datetime.now().strftime('%d.%m.%Y %H:%M'), "%d.%m.%Y %H:%M")

		#Check timestamp of all elements. If timestamp equals current time or is older than current time send the reminder
		for reminder in reminder_list:
			reminder_time = datetime.strptime(reminder[1], "%d.%m.%Y %H:%M")

			reminder_timedelta = reminder_time - current_time
			if reminder_timedelta <= timedelta(0):
				context.job.context['reminder_id'] = reminder[0]
				send_reminder(context, reminder[3])

	#re-schedule job for 1m
	context.job_queue.run_once(check_reminder_list, 60, context=context.job.context)

def get_reminder_id_from_message(message):
	#message is of form
	#/dismiss <id>
	try:
		tokens = message.split(' ')
		id = int(tokens[1])
		return id
	except IndexError as exception:
		return -1
	except Exception as exception:
		log_error(exception)
		return -1

def delete_reminder(id):
	retval = False
	try:
		#CSV shall be opened with newline=''
		#https://docs.python.org/3.8/library/csv.html#csv.reader
		with open('reminders.csv', 'r', newline='') as file_read, open('tmp.csv', 'w', newline='') as file_write:
			reader = csv.reader(file_read, delimiter=',')
			writer = csv.writer(file_write, delimiter=',')
			for row in reader:
				if int(row[0]) == id:
					logging.info("Deleting reminder with ID %i from list", id)
					retval = True
				else:
					writer.writerow(row)
			
		#finally move temporary file 
		shutil.move('tmp.csv', 'reminders.csv')
			
	except Exception as exception:
		log_error(exception)
		retval = False
	finally:
		if not retval:
			logging.warning("Tried to delete ID %d but could not find matching entry.", id)
		return retval

#/start command
def start(update, context):

	#out user details
	logging.info("Command /start received from user: %s with chat_id: %s - Message %s", str(update.message.from_user.username), update.message.chat_id, update.message.text)

	#send personalized welcome message to user (if user got a username), else send default welcome message
	if update.message.from_user.username is not None:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Hi "+str(update.message.from_user.username)+", i am a bot to remind you of things you would else forget.\nTo get a list of my commands please send me  a /help message.")
	else:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Hi, i am a bot to remind you of things you would else forget.\nTo get a list of my commands please send me  a /help message.")

#/dismiss command
def dismiss(update, context):

	#out user details
	logging.info("Command /dismiss received from user: %s with chat_id: %s - Message: %s", str(update.message.from_user.username), update.message.chat_id, update.message.text)

	#Search for reminder id in reminder list and delete if exist
	reminder_id = get_reminder_id_from_message(update.message.text)
	if (reminder_id >= 0) and delete_reminder(reminder_id):
		#notify user
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Reminder was dismissed.")
	else:
		#notify user that remider id was not found
		context.bot.sendMessage(chat_id=update.message.chat_id, text=f"Reminder not found. Please check ID.")

def main():

	#Logging-stuff
	logging.basicConfig(filename="InMemoriamBot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	logging.info("InMemoriamBot started.")

	# Create file for reminder list if not exist
	try:
		tmp_file = open('reminders.csv', 'a')
		tmp_file.close()
	except Exception as exception:
		log_error(exception)
		sys.exit(1)

	# Get telegram API token and chat_id of bot owner from file ".bot_credentials"
	try:
		telegram_config = configparser.ConfigParser()
		telegram_config.read("./.bot_credentials")
		telegram_bot_token = telegram_config.get("configuration", "bot_token")
		telegram_bot_owner_chat_id = telegram_config.get("configuration", "bot_owner_chat_id")
	except Exception as exception:
		log_error(exception)
		sys.exit(1)

	try:
		InMemoriamBotUpdater = Updater(token=telegram_bot_token, use_context=True)
		InMemoriamBotDispatcher = InMemoriamBotUpdater.dispatcher
		InMemoriamBot = InMemoriamBotUpdater.bot
	except telegram.error.InvalidToken as exception:
		log_error("Invalid bot API token.")
		sys.exit(1)

	# Register bot commands
	try:
		#/start
		InMemoriamBotDispatcher.add_handler(CommandHandler('start', start))

		#/dismiss
		InMemoriamBotDispatcher.add_handler(CommandHandler('dismiss', dismiss))
	except Exception as exception:
		log_error(exception)
		sys.exit(1)

	# Notify bot owner that bot has started
	try:
		InMemoriamBot.send_message(chat_id=telegram_bot_owner_chat_id, text="InMemoriamBot was started at " + datetime.now().strftime('%d.%m.%Y (%a) at %H:%M:%S'))
	except Exception as exception:
		log_error(exception)
		sys.exit(1)

	#set bot JobQueue to periodically check the reminder list
	job_queue = InMemoriamBotUpdater.job_queue
	job_queue.run_once(check_reminder_list, 1, context={'chat_id' : telegram_bot_owner_chat_id})

	InMemoriamBotUpdater.start_polling()
	InMemoriamBotUpdater.idle()

if __name__ == '__main__':
	main()
