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
from keyboards.markups import get_weather_inline_kb

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
        WeatherInformation = GetWeatherInformation("a9799770-d38f-493e-9b04-6f36e1c35db9", coordinates)
        yandex_url = await WeatherInformation.get_yandex_site_url()
        await Database().sql_weather_add(message.text, coordinates, yandex_url, str(message.from_user.id))

    else:
        await message.answer('Введено не верное название города!', reply_markup=kb_main)
    await state.finish()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('weather '))
async def weather_query_handler(call: types.CallbackQuery):
    call_data = call.data.replace('weather ', '')
    coordinates = await Database().get_all_row_in_table_where(
        'weather', 'coordinates', 'user_id', str(call.from_user.id)
    )
    WeatherInformation = GetWeatherInformation("a9799770-d38f-493e-9b04-6f36e1c35db9", coordinates[0][0])
    url = await Database().get_all_row_in_table_where("weather", "yandex_url", "user_id", str(call.from_user.id))
    print(call_data)
    if call_data == 'fact':
        await call.answer('Информация о погоде сейчас')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_current_weather()}', reply_markup=get_weather_inline_kb(call, url))

    if call_data == 'today':
        await call.answer('Информация о погоде сегодня')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_day_weather("0")}', reply_markup=get_weather_inline_kb(call, url))
    if call_data == 'tomorrow':
        await call.answer('Информация о погоде завтра')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_day_weather("1")}', reply_markup=get_weather_inline_kb(call, url))



async def get_weather(message: types.Message):
    coordinates = await Database().get_all_row_in_table_where(
        'weather', 'coordinates', 'user_id', str(message.from_user.id))
    #api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
    WeatherInformation = GetWeatherInformation("a9799770-d38f-493e-9b04-6f36e1c35db9", coordinates[0][0])
    url = await Database().get_all_row_in_table_where("weather", "yandex_url", "user_id", str(message.from_user.id))
    try:
        await message.answer(f'{await WeatherInformation.get_current_weather()}', reply_markup=get_weather_inline_kb(
            message, url))
    except KeyError:
        await message.answer(f'По техническим причинам, раздел погоды не доступен')


#async def user_set_notification(message: types.Message):








def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(add_city, state=weather_states.AddCity.set_city)
    dp.register_message_handler(get_weather, text_contains=['Погода'])
    #dp.register_message_handler(user_set_notification, text_contains=['Уведомления'])