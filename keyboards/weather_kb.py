from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Погода сегодня')
b2 = KeyboardButton('/На завтра')
b3 = KeyboardButton('/Уведомления')
b4 = KeyboardButton('/Настройки')
b5 = KeyboardButton('/Назад')




kb_weather = ReplyKeyboardMarkup(resize_keyboard=True)

kb_weather.row(b1, b2).add(b3).add(b4).add(b5)