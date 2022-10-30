import requests
from functions import yandex_weather_requests_parameters
from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter
from pprint import pprint


class GetWeatherInformation:
    async def requests_get(self):
        return requests.get("https://api.weather.yandex.ru/v2/forecast?", params={'lat': self.lat,
                                                                                  'lon': self.lon,
                                                                                  'lang': self.lang,
                                                                                  'limit': self.limit,
                                                                                  'hours': self.hours,
                                                                                  'extra': self.extra},
                            headers={'X-Yandex-API-Key': self.apiKey})

    def __init__(self, api_key, coordinates, lang='ru_RU', limit='1', hours='false', extra='false'):
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
        return request.json()["fact"]["temp"]

    async def get_today_weather(self):
        request = await self.requests_get()
        condition = request.json()["fact"]["condition"]
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
        wind_dir = request.json()["fact"]["wind_dir"]
        wind_dir_icon = {'nw': '↖',
                         'n': '⬆',
                         'ne': '↗',
                         'e': '➡',
                         'se': '↘',
                         's': '⬇',
                         'sw': '↙',
                         'w': '⬅',
                         'c': '↔'}
        daytime = request.json()["fact"]["daytime"]
        daytime_icon = {'d': '🌝',
                        'n': '🌚'}
        return f'Погода сейчас:{daytime_icon[daytime]}\n' \
               f'Описание - {condition_text[condition]}{condition_icon[condition]}\n' \
               f'Температура - {request.json()["fact"]["temp"]}°🌡\n' \
               f'Ощущается как - {request.json()["fact"]["feels_like"]}°🌡\n' \
               f'Скорость ветра - {request.json()["fact"]["wind_speed"]}{wind_dir_icon[wind_dir]}м/c\n' \
               f'Влажность - {request.json()["fact"]["humidity"]}%💧'



async def get_coordinates_from_city_name(city_name):
    async with Nominatim(user_agent="notifBot", adapter_factory=AioHTTPAdapter) as geolocator:
        location = await geolocator.geocode(city_name)
        try:
            return f'{str(location.latitude)} {str(location.longitude)}'
        except:
            return False
