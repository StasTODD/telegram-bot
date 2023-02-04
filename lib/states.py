from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesWeather(StatesGroup):
    question_of_date = State()
    query = State()


class Geoposition(StatesGroup):
    position = State()


class BotTechnical(StatesGroup):
    query = State()
    confirm_query = State()


__all__ = ["StatesWeather",
           "Geoposition",
           "BotTechnical"]
