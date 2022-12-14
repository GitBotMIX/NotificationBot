import sqlite3 as sq
from create_bot import bot


class Database:
    def __init__(self):
        self.values_amount = None
        self.service_name = None
        self.value = None

    def sql_start(self):
        global cur, base
        base = sq.connect('Notifications.db')
        cur = base.cursor()
        if base:
            print('Data base connected OK!')
        base.execute('CREATE TABLE IF NOT EXISTS notification_status(youtube TEXT, weather TEXT, user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS'
                     ' youtube(channel_name TEXT, channel_url TEXT, current_video TEXT, user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS'
                     ' weather(city_name TEXT, coordinates TEXT, yandex_url TEXT, timezone TEXT, requests_amount TEXT,'
                     ' user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS weather_notification(time TEXT, status TEXT, user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS weather_api_key(api_key TEXT, user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS account(status TEXT, user_id TEXT)')
        base.commit()
        return self

    async def get_net_value(self, tuple_in_list: list) -> str:
        return tuple_in_list[0][0]
    async def sql_remove_where(self, table, where, where_data):
        cur.execute(f'DELETE FROM {table} WHERE {where} == ?', (str(where_data),))
        base.commit()

    async def sql_remove_where_and(self, table, where, AND, where_data, AND_data):
        cur.execute(f'DELETE FROM {table} WHERE {where} == ? AND {AND} == ?', (str(where_data), str(AND_data),))
        base.commit()


    async def sql_account_add(self, user_id, status='default'):
        self.values_amount = '?, ?'
        self.service_name = 'account'
        await self.sql_add((status, str(user_id),))

    async def sql_youtube_add(self, channel_name, channel_url, current_video, user_id):
        self.values_amount = '?, ?, ?, ?'
        self.service_name = 'youtube'
        await self.sql_add((channel_name, channel_url, current_video, user_id,))

    async def sql_notification_status_add(self, notification_status, user_id):
        self.values_amount = '?, ?, ?'
        self.service_name = 'notification_status'
        await self.sql_add((notification_status, notification_status, user_id,))

    async def sql_weather_update(self, city_name, yandex_url, coordinates, user_id):
        cur.execute(f'UPDATE weather SET city_name == ?, yandex_url == ?, coordinates == ? WHERE user_id == ?',
                    (str(city_name), yandex_url, str(coordinates), str(user_id)))
        base.commit()

    async def sql_weather_notification_update(self, status, time, user_id):
        cur.execute(f'UPDATE weather_notification SET status == ? WHERE time == ? AND user_id == ?',
                    (status, time, user_id,))
        base.commit()
    async def sql_weather_api_key_add(self, api_key: str, user_id: str):
        self.values_amount = '?, ?'
        self.service_name = 'weather_api_key'
        await self.sql_add((api_key, user_id,))

    async def sql_weather_notification_add(self, time, user_id, status='await'):
        self.values_amount = '?, ?, ?'
        self.service_name = 'weather_notification'
        await self.sql_add((time, status, user_id,))
    async def sql_weather_add(self, city_name, coordinates, yandex_url, user_id, timezone='3', requests_amount='0'):
        self.values_amount = '?, ?, ?, ?, ?, ?'
        self.service_name = 'weather'
        await self.sql_add((city_name, coordinates, yandex_url, timezone, requests_amount, user_id,))

    async def sql_add(self, tuple_data):
        cur.execute(f'INSERT INTO {self.service_name} VALUES ({self.values_amount})', tuple_data)
        base.commit()

    async def sql_update(self, table, set, where, set_data, where_data):
        cur.execute(f'UPDATE {table} SET {set} == ? WHERE {where} == ?', (str(set_data), str(where_data),))
        base.commit()
    async def existance_check(self, data):
        if data is None:
            return False
        return True

    async def existance_check_user_id(self, user_id, table='notification_status'):
        check = cur.execute(f'SELECT user_id FROM {table} WHERE user_id == ?',
                                 (str(user_id),)).fetchone()
        return await self.existance_check(check)

    async def get_all_rows_in_table(self, table):
        return cur.execute(f'SELECT * FROM {table}').fetchall()
    async def get_all_row_in_table(self, table, row):
        return cur.execute(f'SELECT {row} FROM {table}').fetchall()

    async def get_all_row_in_table_where(self, table, row, where, where_data):
        return cur.execute(f'SELECT {row} FROM {table} WHERE {where} == ?', (str(where_data),)).fetchall()

    async def divide_row(self, data_rows):
        row = []
        row_second = []
        for i in data_rows:
            row.append(i[0])
            row_second.append(i[1])
        return row, row_second




    async def get_all_rows_in_table_where(self, table, row, row_second,  where, where_data):
        row, row_second = await self.divide_row(cur.execute(
            f'SELECT {row}, {row_second} FROM {table} WHERE {where} == ?',(str(where_data),)).fetchall()
                                                )
        return row, row_second

    async def get_all_row_in_table_where_and(self, table, row, where, AND, where_data, AND_data):
        return cur.execute(f'SELECT {row} FROM {table} WHERE {where} == ? AND {AND} == ?', (str(where_data),
                                                                                            str(AND_data),)).fetchall()


