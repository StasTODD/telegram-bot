#!/home/stastodd/projects/venv_38_telegram-bot/bin/python3.8
import logging

from aiogram import Bot, Dispatcher, executor, types
from helpers import get_api_token


# Get token
api_token_filename = 'tbot_api_token.txt'
API_TOKEN = get_api_token(api_token_filename)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)