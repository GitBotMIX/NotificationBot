from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import youtube_notifications, weather

from keyboards import main_kb
from keyboards.settings_kb import kb_settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




async def get_main_menu_kb(message: types.Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_kb.kb_main)
    current_state = await state.get_state()
    if current_state == None:
        return
    await state.finish()
    await message.reply('*Действие отменено*', parse_mode='markdown')


async def start(message: types.Message):
    await message.answer('летс гоооо', reply_markup=main_kb.kb_main)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(youtube_notifications.choice_youtube, text_contains=['YouTube'])
    dp.register_message_handler(weather.choice_weather, text_contains=['Yandex'])
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(get_main_menu_kb, commands=['назад'], state='*')