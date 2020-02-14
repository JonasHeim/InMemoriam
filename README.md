# InMemoriam - Telegram Reminder Bot
A telegram bot to remind you to anything you need to be reminded of.

## Installation
Python 3 required.
Run pip on the requirements.txt file
```
pip install -r requirements.txt
```

Run the bot via
```
python InMemoriamBot.py
```

## Description

A new reminder can be set by sending a "/new" command together with the reminder text.\
The bot then asks for the time the reminder shall be sent.\
The time can be either:
| Type | Description | Example |
| ---- | ----------- | ------- |
| Timestamp | A specific time and date | 14. May 2020 @ 14:00 <br> 24. December 2070 @ 01:00 |
| Interval | A specific time interval from now within 24h and at least 1 minute in the future | 25 minutes 8 hours | 


The reminder are saved in a local CSV file which is checked by the bot consecutively every minute.\
An entry looks like this:\
```<unique_id>,<time>,<type>,<message>```\
E.g.:\
```0,13.05.2020 12:27,interval,"Buy toilet paper"```\
```1,14.05.2020 14:00,timestamp,"Birthday Grandpa"```

The list is sorted ascending using the date and id.

If a reminder was found it will be sent to the user.\
The user then can dismiss the last reminder. If the reminder is not dismiss within one minute it will be set again according to its type:
* Timestamp: Increment day of reminder. It will be sent again tomorrow.
* Interval: Reset reminder with same interval.

The user can request/list all reminders of a specific day.\
The user can request all reminders within the next 24 hours.\
The user can delete reminders using their unique ID.

Using:
- [Telegram python wrapper](https://github.com/python-telegram-bot/python-telegram-bot) 

The telegram API-Token is read from the file *.bot_credentials*.\
Edit *.bot_credentials_template* to match your credentials and rename to *.bot_credentials*.
```
[configuration]
bot_token = <your-API-token>
bot_owner_chat_id = <chat_id_of_bot_owner>
```

Current implemented commands:
| Command | Description |
| ------- | ----------- |
| /start | Welcome the user and send a list of current available commands |
| /help | Response with a list of current available commands |
| /new | Set a new reminder |
| /dismiss | Dismiss/delete a reminder |
| /list | List all reminders for a specific day or within next 24 hours |