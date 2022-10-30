from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import Database
from notifications import Scheduler
from keyboards.weather_kb import kb_weather
from keyboards.main_kb import kb_main
from functions import YandexWeather
from functions.YandexWeather import GetWeatherInformation

from states import weather_states
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def choice_weather(message: types.Message, state: FSMContext):
    if await Database().get_all_row_in_table_where('weather', 'user_id', 'user_id', str(message.from_user.id)):
        await message.answer('Меню Yandex.Weather', reply_markup=kb_weather)
    else:
        await message.answer(f'Введи название своего города:')
        await weather_states.AddCity.message_one.set()
        await weather_states.AddCity.next()



async def add_city(message: types.Message, state: FSMContext):
    coordinates = await YandexWeather.get_coordinates_from_city_name(message.text)
    if coordinates != False:
        await message.answer('Город сохранен!', reply_markup=kb_weather)
        await Database().sql_weather_add(message.text, coordinates, str(message.from_user.id))
    else:
        await message.answer('Введено не верное название города!', reply_markup=kb_main)
    await state.finish()

    

async def today_weather(message: types.Message):
    coordinates = await Database().get_all_row_in_table_where(
        'weather', 'coordinates', 'user_id', str(message.from_user.id))
    api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
    WeatherInformation = GetWeatherInformation("0ee81c81-7477-4de2-9c5f-9f6f83984176", coordinates[0][0])
    await message.answer(f'{await WeatherInformation.get_today_weather()}')








def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(add_city, state=weather_states.AddCity.set_city)
    dp.register_message_handler(today_weather, text_contains=['Погода сегодня'])