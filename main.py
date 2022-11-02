from aiogram.utils import executor
from create_bot import dp, bot
from data_base.sqlite_db import Database
import asyncio
import aioschedule
from notifications import Scheduler


async def start(*args):
    print('BOT start')
    Database().sql_start()
    asyncio.create_task(Scheduler().make_task())


from handlers import youtube_notifications, weather, currency_notifications, main_menu, account_settings
youtube_notifications.register_handlers_client(dp)
main_menu.register_handlers_client(dp)
weather.register_handlers_client(dp)
account_settings.register_handlers_client(dp)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=start)
