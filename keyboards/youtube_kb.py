from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Добавить канал')
b2 = KeyboardButton('/Удалить канал')
b3 = KeyboardButton('/Назад')


kb_youtube = ReplyKeyboardMarkup(resize_keyboard=True)

kb_youtube.add(b1).add(b2).add(b3)