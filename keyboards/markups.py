from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from data_base.sqlite_db import Database

def get_weather_inline_kb(message, url):

    b1 = InlineKeyboardButton(text='Сейчас', callback_data='weather fact')
    b2 = InlineKeyboardButton(text='Сегодня', callback_data='weather today')
    b3 = InlineKeyboardButton(text='Завтра', callback_data='weather tomorrow')
    b4 = InlineKeyboardButton(text='Ссылка на Яндекс.Погода',
        url=f'{url[0][0]}')
    weather_inline_kb = InlineKeyboardMarkup(resize_keyboard=False)
    return weather_inline_kb.row(b1, b2, b3).add(b4)
