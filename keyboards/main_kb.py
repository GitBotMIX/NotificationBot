from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/YouTube уведомления')


kb_main = ReplyKeyboardMarkup(resize_keyboard=True)

kb_main.add(b1)