from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Погода')
b2 = KeyboardButton('/Уведомления')
b3 = KeyboardButton('/Настройки')
b4 = KeyboardButton('/Назад')




kb_weather = ReplyKeyboardMarkup(resize_keyboard=True)

kb_weather.row(b1, b2).add(b3).add(b4)