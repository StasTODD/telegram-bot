#!/home/stastodd/projects/venv_38_telegram-bot/bin/python3.8
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from buttons import gps_keyboard

# Don't panic about '*', many imports is here but method __all__ on guard :)
from help_functions import *
from privat import *
from exmo import *
from weather import *
from states import *

# Create loop
loop = asyncio.get_event_loop()

# Get api_token and admins_ids
admin_data = get_data_from_yaml("data.yaml")
API_TOKEN = admin_data["api_token"]
# Create admins_id structure: [int, int]
ADMINS_IDS = [list(adm_id.values())[0] for adm_id in [adm_row for adm_row in admin_data["admins_ids"]]]

# Create storage for save message state
storage = MemoryStorage()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, loop=loop, storage=storage)

# Display output information in image (image - True, text - False):
image_output = True


start_string = "/start - initialization message\n\n"\
               "/privat - exchange rates\n\n"\
               "/exmo - crypto exchange rates\n\n"\
               "/weather - weather data\n\n"\
               "/geoposition - take GPS location"\


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
        weather_api = admin_data["api_openweather"]
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
        await message.answer(f"{gps_latitude} {gps_longitude}")
        await state.finish()
    else:
        await state.finish()
        await send_help(message)


@dp.message_handler()
async def send_help(message: types.Message):
    await message.reply(start_string)


if __name__ == "__main__":
    from hendlers import send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)
