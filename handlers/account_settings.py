from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import youtube_notifications, weather
from data_base.sqlite_db import Database

from keyboards.main_kb import kb_main
from keyboards.settings_kb import kb_settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states import weather_states
from functions.YandexWeather import GetWeatherInformation
from functions import YandexWeather
from keyboards.weather_kb import kb_weather


async def get_menu(message: types.Message):
    await message.answer('Меню настроек', reply_markup=kb_settings)


async def set_city_input(message: types.Message):
    await message.answer(f'Введи название своего города:')
    await weather_states.UpdateCity.message_one.set()
    await weather_states.UpdateCity.next()


async def set_city(message: types.Message, state: FSMContext):
    coordinates = await YandexWeather.get_coordinates_from_city_name(message.text)
    if coordinates != False:
        await message.answer('Город обновлен!', reply_markup=kb_weather)
        WeatherInformation = GetWeatherInformation("0ee81c81-7477-4de2-9c5f-9f6f83984176", coordinates)
        yandex_url = await WeatherInformation.get_yandex_site_url()
        await Database().sql_weather_update(message.text, yandex_url, coordinates, str(message.from_user.id))
    else:
        await message.answer('Введено не верное название города!', reply_markup=kb_main)
    await state.finish()





def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(set_city, state=weather_states.UpdateCity.set_city)
    dp.register_message_handler(get_menu, commands=['Настройки'])
    dp.register_message_handler(set_city_input, text_contains=['Изменить город'])