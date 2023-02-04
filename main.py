#!/home/stastodd/projects/telegram-bot/venv/bin/python3.8

import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sys import exit

# Don't panic about '*', many imports is here but method __all__ on guard :)
from lib.help_functions import *
from lib.buttons import gps_keyboard
from lib.privat import *
from lib.exmo import *
from lib.weather import *
from lib.states import *
from lib.info_about import *

# Get configuration parameters from data.yaml:
config_data = get_data_from_yaml("data.yaml")
# API telegram token:
API_TOKEN = config_data["api_telegram_token"]
# List of admin users. Create admins_id structure: [int, int]
ADMINS_IDS = [list(adm_id.values())[0] for adm_id in [adm_row for adm_row in config_data["admins_ids"]]]

# Create loop
loop = asyncio.get_event_loop()

# Create storage for save message state
storage = MemoryStorage()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, loop=loop, storage=storage)

# Display output information for privat and exmo services in images (images - True, text - False):
image_output = True


start_string = "/start - initialization message\n\n" \
               "/privat - exchange rates\n\n" \
               "/exmo - crypto exchange rates\n\n" \
               "/weather - weather data\n\n" \
               "/geoposition - take GPS location\n\n" \
               "/bot - technical commands"


@dp.message_handler(commands=["start"])
@admin_check(ADMINS_IDS)
async def send_welcome(message: types.Message, **kwargs):
    first_name = message._values["from"].first_name
    last_name = message._values["from"].last_name
    username = message._values["from"].username
    hello_str = "Welcome "
    if first_name:
        hello_str += f"{first_name} "
    if last_name:
        hello_str += f"{last_name} "
    if username:
        hello_str += f"as @{username} "
    await message.answer(hello_str + "in StasTODD Telegram bot")
    await message.answer(start_string)


@dp.message_handler(commands=["privat"])
@admin_check(ADMINS_IDS)
async def send_privatbank(message: types.Message, **kwargs):
    request_result = await get_jsons_privat(url_privatbank_list)
    data_list = await parse_privat_jsons(request_result)

    if image_output:
        result_message = await create_privat_currency_message(data_list, text_for_image=True)
        image_path = await create_privat_image(result_message)
        if image_path:
            with open(image_path, "rb") as image:
                await message.reply_photo(image.read())
        else:
            await message.answer("Image not created. Something wrong...")
    else:
        result_message = await create_privat_currency_message(data_list, text_for_image=False)
        await message.answer(result_message)


@dp.message_handler(commands=["exmo"])
@admin_check(ADMINS_IDS)
async def send_exmo(message: types.Message, **kwargs):
    request_result = await get_json_from_web(url_exmo)
    request_result = await parse_exmo_jsons(request_result, cripto_pair)

    if image_output:
        result_message = await create_cryptocurrency_message(request_result, text_for_image=True)
        image_path = await create_cryptocurrency_image(result_message)
        if image_path:
            with open(image_path, "rb") as image:
                await message.reply_photo(image.read())
        else:
            await message.answer("Image not created. Something wrong...")
    else:
        result_message = await create_cryptocurrency_message(request_result, text_for_image=False)
        await message.answer(result_message)


@dp.message_handler(commands=["weather"], state=None)
@admin_check(ADMINS_IDS)
async def query_weather(message: types.Message, **kwargs):
    await StatesWeather.question_of_date.set()
    await bot.send_message(message.chat.id, "Set weather date:\n"
                                            "/now\n\n"
                                            "/today\n\n"
                                            "/tomorrow\n\n"
                                            "/plus_2_days\n\n"
                                            "/plus_3_days\n\n"
                                            "/plus_4_days")


@dp.message_handler(commands=["now", "today", "tomorrow", "plus_2_days", "plus_3_days", "plus_4_days"],
                    state=StatesWeather.question_of_date)
@admin_check(ADMINS_IDS)
async def query_weather(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data({"weather_date": message.text})
    await StatesWeather.query.set()
    await bot.send_message(message.chat.id, "Push the button and send GPS position", reply_markup=gps_keyboard)


@dp.message_handler(content_types=["any"], state=StatesWeather.query)
@admin_check(ADMINS_IDS)
async def location(message: types.Message, state: FSMContext, **kwargs):
    if message.location is not None:
        weather_api = config_data["api_openweather"]
        weather_date = await state.get_data()
        weather_date = weather_date.get("weather_date")
        if weather_date in ["/today", "/tomorrow", "/plus_2_days", "/plus_3_days", "/plus_4_days"]:
            weather_data = await get_weather_data(weather_api, message.location, state="forecast", lang="en")
        else:
            weather_data = await get_weather_data(weather_api, message.location, state="weather", lang="en")
        weather_message = await create_weather_message(weather_data, weather_date)
        await state.finish()
        await message.answer(weather_message)
    else:
        await state.finish()
        await send_help(message)


@dp.message_handler(commands=["geoposition"], state=None)
@admin_check(ADMINS_IDS)
async def send_location(message: types.Message, state: FSMContext, **kwargs):
    await Geoposition.position.set()
    await bot.send_message(message.chat.id, "Push the button and send geoposition", reply_markup=gps_keyboard)


@dp.message_handler(content_types=["any"], state=Geoposition.position)
@admin_check(ADMINS_IDS)
async def location(message: types.Message, state: FSMContext, **kwargs):
    if message.location is not None:
        gps_latitude = str(message.location.latitude)
        gps_longitude = str(message.location.longitude)
        await message.answer(f"<code>{gps_latitude} {gps_longitude}</code>", parse_mode="html")
        await state.finish()
    else:
        await state.finish()
        await send_help(message)


@dp.message_handler(commands=["bot"], state=None)
@admin_check(ADMINS_IDS)
async def technical_actions(message: types.Message, **kwargs):
    await BotTechnical.query.set()
    await bot.send_message(message.chat.id, "Set the action\n"
                                            "/info - information about bot\n\n"
                                            "/stop_functionality - stop functionality\n\n"
                                            "/future - other future actions")


@dp.message_handler(commands=["info"], state=BotTechnical.query)
@admin_check(ADMINS_IDS)
async def data_platform(message: types.Message, state: FSMContext, **kwargs):
    await state.finish()
    info_message = await all_messages_text()
    await bot.send_message(message.chat.id, info_message, parse_mode="html")


@dp.message_handler(commands=["stop_functionality"], state=BotTechnical.query)
@admin_check(ADMINS_IDS)
async def stop_bot_question(message: types.Message, state: FSMContext, **kwargs):
    await BotTechnical.confirm_query.set()
    await bot.send_message(message.chat.id, "You really sure?\n"
                                            "/stop_bot - stop bot process\n\n"
                                            "/stop_camera - stop camera process\n\n"
                                            "/back - back to previous menu")


@dp.message_handler(commands=["stop_bot"], state=BotTechnical.confirm_query)
@admin_check(ADMINS_IDS)
async def stop_bot_action(message: types.Message, state: FSMContext, **kwargs):
    await bot.send_message(message.chat.id, "⛔⛔⛔\n"
                                            "At this moment, python telegram bot stopping with sys.exit()\n"
                                            "⛔⛔⛔")
    exit()


@dp.message_handler(commands=["stop_camera"], state=BotTechnical.confirm_query)
@admin_check(ADMINS_IDS)
async def stop_camera_action(message: types.Message, state: FSMContext, **kwargs):
    await state.finish()
    # attribute it is a keyword for find PID process in the system:
    attribute = "rpi_pirsensor_camera_telegram"
    pid = await find_pid(attribute)
    # When PID is existed and correct:
    if isinstance(pid, int) and pid != 0:
        await bot.send_message(message.chat.id, f"⛔⛔⛔\n"
                                                f"At this moment, camera's PID '{pid}' is stopping with 'kill -9'\n"
                                                f"⛔⛔⛔")
        kill_status = await kill_process(pid)
        # When PID can't be killed:
        if isinstance(kill_status, str):
            await bot.send_message(message.chat.id, f"PID '{pid}' can't be killed, error:\n\n{kill_status}")
    # When got error message:
    elif isinstance(pid, str):
        await bot.send_message(message.chat.id, f"PID not detected. Error was registered:\n\n{pid}")
    # When PID not found:
    else:
        await bot.send_message(message.chat.id, "Camera's PID not found or not connected to the server")


@dp.message_handler(commands=["back"], state=BotTechnical.confirm_query)
@admin_check(ADMINS_IDS)
async def back_to_technical_actions(message: types.Message, state: FSMContext, **kwargs):
    await state.finish()
    await technical_actions(message)


@dp.message_handler(commands=["future"], state=BotTechnical.query)
@admin_check(ADMINS_IDS)
async def future_command(message: types.Message, state: FSMContext, **kwargs):
    await state.finish()
    await bot.send_message(message.chat.id, "About future functions, see:\n"
                                            "https://github.com/StasTODD/telegram-bot")
    await bot.send_message(message.chat.id, start_string)


@dp.message_handler()
async def send_help(message: types.Message):
    await message.reply(start_string)


if __name__ == "__main__":
    from lib.hendlers import send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)
