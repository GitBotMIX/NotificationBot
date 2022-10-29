from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Добавить канал')
b2 = KeyboardButton('/Удалить канал')
b3 = KeyboardButton('/Настройка уведомлений')
b4 = KeyboardButton('/Назад')


kb_youtube = ReplyKeyboardMarkup(resize_keyboard=True)

kb_youtube.row(b1, b2).add(b3).add(b4)