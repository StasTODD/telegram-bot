from aiogram import types


gps_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
gps_button = types.KeyboardButton(text="send geoposition", request_location=True)
gps_keyboard.add(gps_button)


__all__ = ["gps_keyboard"]
