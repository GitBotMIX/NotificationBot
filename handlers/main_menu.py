from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import youtube_notifications

from keyboards import main_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_main_menu_kb(message: types.Message):
    await message.answer('Главное меню', reply_markup=main_kb.kb_main)
async def start(message: types.Message):
    await message.answer('летс гоооо', reply_markup=main_kb.kb_main)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(youtube_notifications.choice_youtube, text_contains=['YouTube'])
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(get_main_menu_kb, commands=['назад'])