from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Изменить город')
b2 = KeyboardButton('/Назад')





kb_settings = ReplyKeyboardMarkup(resize_keyboard=True)

kb_settings.add(b1).add(b2)