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

def get_weather_notification_kb(notification_status):
    weather_inline_kb = InlineKeyboardMarkup(resize_keyboard=False)
    weather_inline_kb.row_width = 4
    notification_user_array = {'ON': 'Выключить', 'OFF': 'Включить'}
    notification_array = {'ON': 'OFF', 'OFF': 'ON'}
    b1 = InlineKeyboardButton(text='Удалить уведомление', callback_data='weather_notif_delete')
    b2 = InlineKeyboardButton(
        text=f'{notification_user_array[notification_status]} уведомления',
        callback_data=f'weather_notif_upd {notification_array[notification_status]}')
    button_list = []
    for i in range(0, 24):
        s = f'{i}:00'
        if len(s) == 4:
            button_list.append('0' + s)
        else:
            button_list.append(s)
    weather_inline_kb.add(*[InlineKeyboardButton(
        el, callback_data=f'weather_notif {str(index)}') for index, el in enumerate(button_list)])
    weather_inline_kb.add(b1).add(b2)
    return weather_inline_kb