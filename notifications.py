import aioschedule
import asyncio
from functions import youtube_url
from data_base.sqlite_db import Database
from create_bot import dp, bot
import datetime
import time
from functions.YandexWeather import GetWeatherInformation



class Scheduler:
    async def make_task(self):
        aioschedule.every(30).seconds.do(self.youtube_video_listen)
        aioschedule.every(10).seconds.do(self.send_weather_notification)
        #aioschedule.every(5).seconds.do(self.display_notification)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def remove_repeated_user_id(self, all_user_id):
        updated_user_id_list = []
        for i in all_user_id:
            if i[0] not in updated_user_id_list:
                updated_user_id_list.append(i[0])
        return updated_user_id_list

    async def unix_to_gmt_time(self, unix_time: int) -> int:
        time = datetime.datetime.utcfromtimestamp(unix_time)
        return int(time.strftime('%H'))

    async def check_user_account_status(self, user_id):
        user_account_status = await Database().get_all_row_in_table_where('account', 'status', 'user_id', user_id)
        if user_account_status[0][0] == 'default':
            requests_amount = await Database().get_all_row_in_table_where('weather', 'requests_amount', 'user_id',
                                                                          user_id)
            if int(requests_amount[0][0]) >= 10:
                await bot.send_message(user_id,
                    'Превышен лимит суточных запросов для бесплатного акаунта, что-бы смотреть погоду чаще, '
                    'необходимо преобрести премиум, что-бы преобрести премиум, воспользуйся командой'
                    ' - /get_premium')
                return False
            await Database().sql_update('weather', 'requests_amount', 'user_id', int(requests_amount[0][0]) + 1,
                                        user_id)
        return True

    async def send_weather_notification(self):
        weather_notification_list = await Database().get_all_rows_in_table('weather_notification')
        for listEl in weather_notification_list:
            if not weather_notification_list:
                return
            user_id = listEl[2]
            send_status = listEl[1]
            notification_time = listEl[0]
            notification_status = await Database().get_all_row_in_table_where_and(
                'notification_status', 'weather', 'weather', 'user_id', 'ON', user_id)
            if not notification_status:
                continue
            current_hour_utc = await self.unix_to_gmt_time(int(time.time()))
            timezone = await Database().get_all_row_in_table_where(
                'weather', 'timezone', 'user_id', user_id)
            cur_user_time = current_hour_utc + int(timezone[0][0])
            if send_status == 'await':
                if cur_user_time == int(notification_time):
                    await Database().sql_weather_notification_update(
                        str(cur_user_time-1), notification_time, user_id)

                    coordinates = await Database().get_all_row_in_table_where(
                        'weather', 'coordinates', 'user_id', user_id)
                    api_key = await Database().get_all_row_in_table('weather_api_key', 'api_key')
                    try:
                        WeatherInformation = GetWeatherInformation(api_key[0][0], coordinates[0][0])
                    except IndexError:
                        await bot.send_message(user_id, 'api-key is not valid')
                        return
                    if not await self.check_user_account_status(user_id):
                        return
                    await bot.send_message(user_id, f'{await WeatherInformation.get_current_weather_short()}')
                    continue
                else:
                    continue
            if cur_user_time == int(send_status):
                await Database().sql_weather_notification_update(
                    'await', notification_time, user_id)
                continue






    async def youtube_video_listen(self):
        all_user_id = await self.remove_repeated_user_id(await Database().get_all_row_in_table('youtube', 'user_id'))
        for user_id in all_user_id:
            youtube_channel_url, youtube_channel_name = await Database().get_all_rows_in_table_where('youtube',
                                                                               'channel_url',
                                                                               'channel_name',
                                                                               'user_id',
                                                                               user_id)
            for yc in range(len(youtube_channel_url)):
                parse_video_url = await youtube_url.parse_videos(youtube_channel_url[yc])
                old_parse_video_url = await Database().get_all_row_in_table_where_and('youtube',
                    'current_video', 'channel_url', 'user_id', youtube_channel_url[yc], user_id)
                if parse_video_url != old_parse_video_url[0][0]:
                    try:
                        await bot.send_message(user_id, f'На канале "{youtube_channel_name[yc]}" новое видео\n'
                                                        f'https://www.youtube.com/watch?v={parse_video_url}')
                        await Database().sql_update('youtube', 'current_video', 'current_video', parse_video_url,
                                                    old_parse_video_url[0][0])
                    except: #ChatNotFound
                        await Database().sql_remove_where('youtube', 'user_id', user_id)
                        await Database().sql_remove_where('notification_status', 'user_id', user_id)
                        print('X')
                        break
                else:
                    print('<')



