from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesWeather(StatesGroup):
    question_of_date = State()
    query = State()
