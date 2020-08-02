<h1 align="center">Telegram bot </h1>

Private Telegram bot with little functional. General idea it's telegram-interface for work with different program and RaspberryPI hardware modules. Bot was wrote use python-async methods and this approach do program faster where run I/O operations.

It's private little project for helping me in my life. If become new necessaryes, the bot will be supplemented with new functionality. 

## Functional:

✔️ Get info about API token and admins id from yaml-file. 

✔️ Send message to admin(s) if telegram bot was started.

✔️ Admin(s) ID checker in decorator. It splitting clients privileges.

✔️ Work with [Privatbank](https://privatbank.ua/) API for check USD/UAH course.

✔️ Work with [Exmo](https://exmo.com/) cryptoexchange API for check BTC/USD course.

✔️ Privatbank and Exmo have reply-format in the image.

✔️ Work with [openweathermap](https://openweathermap.org/) API for weather check.

✔️ Send geoposition in chat - get coordinates in text format.

✔️ Send software/hardware platform info where it was started. 

✔️ Bot-command for stop Telegram bot process.

### Starting message has view:

![](images/README/start.jpg)

Detail of [bot-functional and examples](README/bot_general_overview.md) of run commands result.

### In the future, will be support this functions:
❔ Work with RaspberryPI hardware modules.

❔ Work with SQLite DB for save data.

## Installing procedure:

- Clone or download project from github.
- Install python version 3.7+.
- Create and activate special venv for project:

`username@linux:~$ python3.7 -m venv venv_telegram_bot`

`username@linux:~$ source venv_telegram_bot/bin/activate`

- Upgrade `setuptools` and `wheel` libs:

`(venv_telegram_bot) username@linux:~$ pip install --upgrade pip setuptools wheel`

- Install necessary packages from `requirements.txt`:

`(venv_telegram_bot) username@linux:~$ pip install -r proj/requirements.txt` 

- Start Bot:

`(venv_telegram_bot) username@linux:~$ python main.py`

NOTE: main.py:1 should most likely be edited to fit your paths