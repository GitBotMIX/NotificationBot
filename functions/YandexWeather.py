import requests
from functions import yandex_weather_requests_parameters
from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter
from pprint import pprint
import datetime
from data_base.sqlite_db import Database



class GetWeatherInformation:
    async def requests_get(self):
        return requests.get("https://api.weather.yandex.ru/v2/forecast?", params={'lat': self.lat,
                                                                                  'lon': self.lon,
                                                                                  'lang': self.lang,
                                                                                  'limit': self.limit,
                                                                                  'hours': self.hours,
                                                                                  'extra': self.extra},
                            headers={'X-Yandex-API-Key': self.apiKey})

    def __init__(self, api_key, coordinates, lang='ru_RU', limit='3', hours='true', extra='false'):
        coordinates_list = coordinates.split(' ')
        print(coordinates_list)
        self.lat = coordinates_list[0]
        self.lon = coordinates_list[1]
        self.lang = lang
        self.limit = limit
        self.hours = hours
        self.extra = extra
        self.apiKey = api_key

    async def get_current_temperature(self):
        request = await self.requests_get()
        return request.json()

    async def get_condition_now_day(self, request):
        morning = request.json()["forecasts"][0]["hours"][7]["condition"]
        dinner = request.json()["forecasts"][0]["hours"][14]["condition"]
        evening = request.json()["forecasts"][0]["hours"][19]["condition"]
        night = request.json()["forecasts"][0]["parts"]["night_short"]
        return morning, dinner, evening, night

    async def get_weather_arrays(self):
        condition_text = {'clear': 'ясно',
                              'partly-cloudy': 'малооблачно',
                              'cloudy': 'облачно с прояснениями',
                              'overcast': 'пасмурно',
                              'drizzle': 'морось',
                              'light-rain': 'небольшой дождь',
                              'rain': 'дождь',
                              'moderate-rain': 'умеренный дождь',
                              'heavy-rain': 'сильный дождь',
                              'continuous-heavy-rain': 'сильный дождь',
                              'showers': 'ливень',
                              'wet-snow': 'дождь со снегом',
                              'light-snow': 'небольшой снег',
                              'snow': 'снег',
                              'snow-showers': 'снегопад',
                              'hail': 'град',
                              'thunderstorm': 'гроза',
                              'thunderstorm-with-rain': 'дождь с грозой',
                              'thunderstorm-with-hail': 'гроза с градом'}
        condition_icon = {'clear': '☀',
                              'partly-cloudy': '🌤',
                              'cloudy': '🌥',
                              'overcast': '☁',
                              'drizzle': '🌦',
                              'light-rain': '🌦',
                              'rain': '🌧',
                              'moderate-rain': '🌧',
                              'heavy-rain': '🌧',
                              'continuous-heavy-rain': '🌧',
                              'showers': '☔',
                              'wet-snow': '🌧🌨',
                              'light-snow': '🌨',
                              'snow': '🌨',
                              'snow-showers': '🌨❄',
                              'hail': '🌧❄',
                              'thunderstorm': '🌩',
                              'thunderstorm-with-rain': '⛈',
                              'thunderstorm-with-hail': '⛈❄'}
        wind_dir_icon = {'nw': '↖',
                             'n': '⬆',
                             'ne': '↗',
                             'e': '➡',
                             'se': '↘',
                             's': '⬇',
                             'sw': '↙',
                             'w': '⬅',
                             'c': '↔'}
        daytime_icon = {'d': '🌝',
                        'n': '🌚'}
        return condition_text, condition_icon, wind_dir_icon, daytime_icon

    async def get_request_json(self, request, obj, day):
        return request.json()[obj][int(day)]

    async def get_weather_info_prec_period(self, request, time):
        obj = 'forecasts'
        time = int(time)
        request_json = await self.get_request_json(request, obj, '0')
        prec_type = request_json['hours'][time]["prec_type"]

        return prec_type

    async def get_yandex_site_url(self):
        request = await self.requests_get()
        return request.json()['info']["url"]

    async def prec_for_time_check(self, request, hour: int):
        hour_one = await self.get_weather_info_prec_period(request, hour)
        print(hour_one)
        if hour_one != 0:
            return hour_one, 1
        else:
            if hour <= 22:
                hour_two = await self.get_weather_info_prec_period(request, hour + 1)
                if hour_two != 0:
                    return hour_two, 2
                else:
                    if hour <= 21:
                        hour_three = await self.get_weather_info_prec_period(request, hour + 2)
                        if hour_three != 0:
                            return hour_three, 3
                        else:
                            return False, False
                    else:
                        return False, False
            else:
                return False, False

    async def get_current_weather_short(self):
        request = await self.requests_get()
        current_hour = await self.get_current_hour(request)
        #current_hour = 8

        temperature, temperature_feels_like, wind_speed,\
        humidity, wind_dir, condition = await self.get_weather_info_fact(request)
        condition_it_raining = ['drizzle', 'light-rain', 'rain', 'moderate-rain', 'heavy-rain', 'continuous-heavy-rain',
                                'showers', 'wet-snow', 'light-snow', 'snow', 'snow-showers', 'hail',
                                'thunderstorm-with-rain', 'thunderstorm-with-hail']
        condition_text, condition_icon, wind_dir_icon, daytime_icon = await self.get_weather_arrays()
        if condition in condition_it_raining:
            prec_text = ''
        else:
            prec_type_text_array = {1: 'дождь', 2: 'дождь со снегом', 3: 'снег', 4: 'град'}
            prec_type_symbol_array = {1: '☔', 2: '☔', 3: '☃', 4: '☄'}
            prec_for_time, prec_for_time_hour = await self.prec_for_time_check(request, int(current_hour))
            if prec_for_time:
                if prec_for_time_hour == 1:
                    prec_text = f'{prec_type_symbol_array[prec_for_time]}' \
                                f'В течение часа ожидается {prec_type_text_array[prec_for_time]}'
                else:
                    prec_text = f'{prec_type_symbol_array[prec_for_time]}' \
                                f'В ближайшие {prec_for_time_hour} часа ожидается {prec_type_text_array[prec_for_time]}'
            else:
                prec_text = f'⛱В ближайшие 3 часа осадков не ожидается '
        return await self.get_weather_text_fact_short(condition_icon, condition, temperature,
                               temperature_feels_like, wind_dir_icon, wind_dir, wind_speed, prec_text)
    async def get_current_weather(self):
        request = await self.requests_get()
        current_hour = await self.get_current_hour(request)
        #current_hour = 8

        temperature, temperature_feels_like, wind_speed,\
        humidity, wind_dir, condition = await self.get_weather_info_fact(request)
        condition_it_raining = ['drizzle', 'light-rain', 'rain', 'moderate-rain', 'heavy-rain', 'continuous-heavy-rain',
                                'showers', 'wet-snow', 'light-snow', 'snow', 'snow-showers', 'hail',
                                'thunderstorm-with-rain', 'thunderstorm-with-hail']
        condition_text, condition_icon, wind_dir_icon, daytime_icon = await self.get_weather_arrays()
        if condition in condition_it_raining:
            prec_text = ''
        else:
            prec_type_text_array = {1: 'дождь', 2: 'дождь со снегом', 3: 'снег', 4: 'град'}
            prec_type_symbol_array = {1: '☔', 2: '☔', 3: '☃', 4: '☄'}
            prec_for_time, prec_for_time_hour = await self.prec_for_time_check(request, int(current_hour))
            if prec_for_time:
                if prec_for_time_hour == 1:
                    prec_text = f'{prec_type_symbol_array[prec_for_time]}' \
                                f'В течение часа ожидается {prec_type_text_array[prec_for_time]}'
                else:
                    prec_text = f'{prec_type_symbol_array[prec_for_time]}' \
                                f'В ближайшие {prec_for_time_hour} часа ожидается {prec_type_text_array[prec_for_time]}'
            else:
                prec_text = f'⛱В ближайшие 3 часа осадков не ожидается '
        return await self.get_weather_text_fact(condition_icon, condition_text, condition, temperature,
                               temperature_feels_like, wind_dir_icon, wind_dir, wind_speed, humidity, prec_text)

    async def get_day_weather(self, day):
        request = await self.requests_get()
        request_json = await self.get_request_json(request, 'forecasts', f'{day}')
        tm, tflm, wsm, hm, wdm, cm = await self.get_weather_info_parts(request_json, 'morning')
        td, tfld, wsd, hd, wdd, cd = await self.get_weather_info_parts(request_json, 'day')
        te, tfle, wse, he, wde, ce = await self.get_weather_info_parts(request_json, 'evening')
        tn, tfln, wsn, hn, wdn, cn = await self.get_weather_info_parts(request_json, 'night')
        condition_text, condition_icon, wind_dir_icon, daytime_icon = await self.get_weather_arrays()
        days_array = {'0': 'сегодня',
                      '1': 'завтра',
                      '2': 'послезавтра'}
        return f'Погода {days_array[day]}:\n' \
               f'   Утро:\n' \
               f'       {condition_icon[cm]}{condition_text[cm].title()}\n' \
               f'       🌡{tm}°({tflm}°)\n' \
               f'       {wind_dir_icon[wdm]}{wsm}м/c\n' \
               f'       💧{hm}%\n' \
               f'   День:\n' \
               f'       {condition_icon[cd]}{condition_text[cd].title()}\n' \
               f'       🌡{td}°({tfld}°)\n' \
               f'       {wind_dir_icon[wdd]}{wsd}м/c\n' \
               f'       💧{hd}%\n' \
               f'   Вечер:\n' \
               f'       {condition_icon[ce]}{condition_text[ce].title()}\n' \
               f'       🌡{te}°({tfle}°)\n' \
               f'       {wind_dir_icon[wde]}{wse}м/c\n' \
               f'       💧{he}%\n' \
               f'   Ночь:\n' \
               f'       {condition_icon[cn]}{condition_text[cn].title()}\n' \
               f'       🌡{tn}°({tfln}°)\n' \
               f'       {wind_dir_icon[wdn]}{wsn}м/c\n' \
               f'       💧{hn}%\n'

    async def get_weather_text_fact(self, condition_icon, condition_text, condition, temperature,
                               temperature_feels_like, wind_dir_icon, wind_dir, wind_speed, humidity, prec_text):
        return f'Сейчас:\n\n' \
               f'   {condition_icon[condition]}{condition_text[condition].title()}\n' \
               f'   🌡{temperature}°({temperature_feels_like}°)\n' \
               f'   {wind_dir_icon[wind_dir]}{wind_speed}м/c\n' \
               f'   💧{humidity}%\n\n' \
               f'   {prec_text}'

    async def get_weather_text_fact_short(self, condition_icon, condition, temperature,
                               temperature_feels_like, wind_dir_icon, wind_dir, wind_speed, prec_text):
        return f'Сейчас: {condition_icon[condition]}; 🌡{temperature}°({temperature_feels_like}°); ' \
               f'{wind_dir_icon[wind_dir]}{wind_speed}м/c;\n{prec_text}'
    async def get_weather_info_parts(self, request_json, part_name):
        temperature = request_json['parts'][part_name]["temp_avg"]
        temperature_feels_like = request_json['parts'][part_name]["feels_like"]
        wind_speed = request_json['parts'][part_name]["wind_speed"]
        humidity = request_json['parts'][part_name]["humidity"]
        wind_dir = request_json['parts'][part_name]["wind_dir"]
        condition = request_json['parts'][part_name]["condition"]
        return temperature, temperature_feels_like, wind_speed, humidity, wind_dir, condition

    async def get_weather_info_fact(self, request):
        temperature = request.json()['fact']["temp"]
        temperature_feels_like = request.json()['fact']["feels_like"]
        wind_speed = request.json()['fact']["wind_speed"]
        humidity = request.json()['fact']["humidity"]
        wind_dir = request.json()['fact']["wind_dir"]
        condition = request.json()['fact']["condition"]
        return temperature, temperature_feels_like, wind_speed, humidity, wind_dir, condition

    async def get_current_hour(self, request):
        data = request.json()['now']
        timestamp = data
        value = datetime.datetime.fromtimestamp(timestamp)
        return value.strftime('%H')


async def get_coordinates_from_city_name(city_name):
    async with Nominatim(user_agent="notifBot", adapter_factory=AioHTTPAdapter) as geolocator:
        location = await geolocator.geocode(city_name)
        try:
            return f'{str(location.latitude)} {str(location.longitude)}'
        except:
            return False


async def list_tuple_to_list_str(list_tuple: list) -> list:
    new_list = []
    for i in list_tuple:
        new_list.append(i[0])
    return new_list


