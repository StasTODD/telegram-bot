from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesWeather(StatesGroup):
    query = State()


