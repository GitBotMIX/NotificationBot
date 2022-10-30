from aiogram.dispatcher.filters.state import State, StatesGroup


class AddCity(StatesGroup):
    message_one = State()
    set_city = State()