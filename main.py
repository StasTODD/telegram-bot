#!/home/stastodd/projects/venv_38_telegram-bot/bin/python3.8
import logging

from aiogram import Bot, Dispatcher, executor, types
from help_functions import get_data_from_yaml, admin_check, get_jsons_privat, parse_privat_jsons
import asyncio

from typing import List, Dict, Union, Any


# Create loop
loop = asyncio.get_event_loop()

# Get api_token and admins_ids
admin_data = get_data_from_yaml('data.yaml')
API_TOKEN = admin_data['api_token']
# Create admins_id structure: [int, int]
ADMINS_IDS = [list(adm_id.values())[0] for adm_id in [adm_row for adm_row in admin_data['admins_ids']]]

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, loop=loop)
# dp = Dispatcher(bot)

# Privatbank API (JSON format)
url_privatbank_private = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
url_privatbank_busines = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
url_privatbank_list = [url_privatbank_private, url_privatbank_busines]


@dp.message_handler(commands=['start'])
@admin_check(ADMINS_IDS)
async def send_welcome(message: types.Message):
    first_name = message._values['from'].first_name
    last_name = message._values['from'].last_name
    username = message._values['from'].username
    hello_str = 'Welcome '
    if first_name:
        hello_str += f'{first_name} '
    if last_name:
        hello_str += f'{last_name} '
    if username:
        hello_str += f'as @{username} '
    await message.answer(hello_str + "in StasTODD Telegram bot")
    await message.answer("/start - initialization message\n"
                         "/privat - exchange rates")


@dp.message_handler(commands=['privat'])
@admin_check(ADMINS_IDS)
async def send_privatbank(message: types.Message):
    await message.answer("START PRIVAT")
    result = await get_jsons_privat(url_privatbank_list)
    result = parse_privat_jsons(result)
    await message.answer("END PRIVAT")


@dp.message_handler()
async def send_help(message: types.Message):
    await message.reply("/start - initialization message")


if __name__ == '__main__':
    from hendlers import send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)
