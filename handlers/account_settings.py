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
    try:
        coordinates = await YandexWeather.get_coordinates_from_city_name(message.text)
        if coordinates:
            await message.answer('Город обновлен!', reply_markup=kb_weather)
            api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
            WeatherInformation = GetWeatherInformation(api_key[0][0], coordinates)
            yandex_url = await WeatherInformation.get_yandex_site_url()
            await Database().sql_weather_update(message.text, yandex_url, coordinates, str(message.from_user.id))
        else:
            await message.answer('Введено не верное название города!', reply_markup=kb_main)
        await state.finish()
    except:
        await message.answer('Превышен лимит запросов, попробуй позже')

async def add_api_key(message: types.Message):
    api_key_data = message.text.replace('Добавить API Ключ: ', '')
    await Database().sql_weather_api_key_add(api_key_data, str(message.from_user.id))
    await message.answer('Добавил ключ!')



def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(set_city, state=weather_states.UpdateCity.set_city)
    dp.register_message_handler(get_menu, commands=['Настройки'])
    dp.register_message_handler(set_city_input, text_contains=['Изменить город'])
    dp.register_message_handler(add_api_key, text_contains=['Добавить API Ключ:'])