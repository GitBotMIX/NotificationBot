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
from keyboards import markups

from states import weather_states
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def choice_weather(message: types.Message):
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
        api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
        try:
            WeatherInformation = GetWeatherInformation(api_key[0][0], coordinates)
        except IndexError:
            await message.answer('api-key is not valid')
            return
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
    api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
    WeatherInformation = GetWeatherInformation(api_key[0][0], coordinates[0][0])
    url = await Database().get_all_row_in_table_where("weather", "yandex_url", "user_id", str(call.from_user.id))
    if call_data == 'fact':
        await call.answer('Информация о погоде сейчас')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_current_weather()}',
            reply_markup=markups.get_weather_inline_kb(call, url))

    if call_data == 'today':
        await call.answer('Информация о погоде сегодня')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_day_weather("0")}',
            reply_markup=markups.get_weather_inline_kb(call, url))
    if call_data == 'tomorrow':
        await call.answer('Информация о погоде завтра')
        await call.message.edit_text(
            text=f'{await WeatherInformation.get_day_weather("1")}',
            reply_markup=markups.get_weather_inline_kb(call, url))


async def get_weather(message: types.Message):
    user_id = message.from_user.id
    exist_user_autorizate = await Database().get_all_row_in_table_where('weather', 'user_id', 'user_id', user_id)
    if not exist_user_autorizate:
        await choice_weather(message)
        return
    coordinates = await Database().get_all_row_in_table_where(
        'weather', 'coordinates', 'user_id', str(user_id))
    api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
    WeatherInformation = GetWeatherInformation(api_key[0][0], coordinates[0][0])
    url = await Database().get_all_row_in_table_where("weather", "yandex_url", "user_id", str(user_id))
    try:
        await message.answer(f'{await WeatherInformation.get_current_weather()}',
                             reply_markup=markups.get_weather_inline_kb(message, url))
    except KeyError:
        await message.answer(f'По техническим причинам, раздел погоды не доступен')


async def user_set_notification(message: types.Message):
    user_id = message.from_user.id
    exist_user_autorizate = await Database().get_all_row_in_table_where('weather', 'user_id', 'user_id', user_id)
    if not exist_user_autorizate:
        await choice_weather(message)
        return
    notification_status = await Database().get_all_row_in_table_where(
        'notification_status', 'weather', 'user_id', user_id)

    if notification_status:
        pass
    else:
        await Database().sql_notification_status_add('ON', user_id)
        notification_status = await Database().get_all_row_in_table_where(
            'notification_status', 'weather', 'user_id', user_id)
    existing_time = await Database().get_all_row_in_table_where('weather_notification', 'time', 'user_id', user_id)
    existing_time = await YandexWeather.list_tuple_to_list_str(existing_time)
    await message.answer("Выбери время ежедневного уведомления о прогнозе",
                         reply_markup=markups.get_weather_notification_kb(notification_status[0][0], existing_time))




@dp.callback_query_handler(lambda x: x.data and x.data.startswith('weather_notif '))
async def weather_add_notification(call: types.CallbackQuery):
    user_id = call.from_user.id
    call_data_list = call.data.split(':')
    call_data = call_data_list[0].replace('weather_notif ', '')
    operation_status = call_data_list[1].replace('operation_status ', '')
    async def get_attr():
        notification_status = await Database().get_all_row_in_table_where(
            'notification_status', 'weather', 'user_id', user_id)
        existing_time = await Database().get_all_row_in_table_where('weather_notification', 'time', 'user_id', user_id)
        existing_time = await YandexWeather.list_tuple_to_list_str(existing_time)
        return notification_status, existing_time

    if operation_status == '+':
        await Database().sql_weather_notification_add(call_data, str(user_id))
        notification_status, existing_time = await get_attr()
        await call.message.edit_text("Выбери время ежедневного уведомления о прогнозе",
                                     reply_markup=markups.get_weather_notification_kb(notification_status[0][0],
                                                                                      existing_time))
    else:
        await Database().sql_remove_where_and('weather_notification', 'user_id', 'time', user_id, call_data)
        notification_status, existing_time = await get_attr()
        await call.message.edit_text("Выбери время ежедневного уведомления о прогнозе",
                                     reply_markup=markups.get_weather_notification_kb(notification_status[0][0],
                                                                                      existing_time))


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('weather_notif_upd '))
async def weather_upd_status_notification(call: types.CallbackQuery):
    call_data = call.data.replace('weather_notif_upd ', '')
    notification_user_array = {'ON': '"включены"', 'OFF': '"выключены"'}
    await call.message.edit_text(f'Уведомления о погоде {notification_user_array[call_data]}')
    await Database().sql_update('notification_status', 'weather', 'user_id', call_data, call.from_user.id)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(add_city, state=weather_states.AddCity.set_city)
    dp.register_message_handler(get_weather, text_contains=['Погода'])
    dp.register_message_handler(user_set_notification, text_contains=['Уведомления'])
