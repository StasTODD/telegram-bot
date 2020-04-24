#!/home/stastodd/projects/venv_38_telegram-bot/bin/python3.8
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from help_functions import \
    get_data_from_yaml, \
    admin_check, \
    get_json_from_web
from privat import \
    get_jsons_privat, \
    parse_privat_jsons, \
    create_currency_message

from exmo import \
    parse_exmo_jsons, \
    create_crypto_currency_message

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

# EXMO exchange API (JSON format)
url_exmo = 'https://api.exmo.com/v1.1/ticker'
cripto_pair = ['BTC_USD', 'ETH_USD', 'XRP_USD', 'EOS_USD',
               'ETC_USD', 'LTC_USD', 'NEO_USD', 'SMART_USD',
               'XEM_USD', 'XLM_USD', 'XMR_USD']


@dp.message_handler(commands=['start'])
@admin_check(ADMINS_IDS)
async def send_welcome(message: types.Message, **kwargs):
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
                         "/privat - exchange rates\n"
                         "/exmo - crypto exchange rates\n"
                         "/test_image - test work with images")


@dp.message_handler(commands=['privat'])
@admin_check(ADMINS_IDS)
async def send_privatbank(message: types.Message, **kwargs):
    result = await get_jsons_privat(url_privatbank_list)
    result = await parse_privat_jsons(result)
    result_message = await create_currency_message(result)
    await message.answer(result_message)


@dp.message_handler(commands=['exmo'])
@admin_check(ADMINS_IDS)
async def send_exmo(message: types.Message, **kwargs):
    result = await get_json_from_web(url_exmo)
    result = await parse_exmo_jsons(result, cripto_pair)
    result_message = await create_crypto_currency_message(result)
    await message.answer(result_message)


@dp.message_handler(commands=['test_image'])
@admin_check(ADMINS_IDS)
async def send_image(message: types.Message, **kwargs):
    # TODO: move work task to another file
    photo = '/home/stastodd/projects/telegram-bot/images/background_template/640x640.png'
    with open(photo, "rb") as f:
        await message.reply_photo(f.read())


@dp.message_handler()
async def send_help(message: types.Message):
    await message.reply("/start - initialization message")


if __name__ == '__main__':
    from hendlers import send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)
