from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_button_type(income_=False):
    interval = InlineKeyboardButton(text='Интервальный', callback_data='interval')
    days = InlineKeyboardButton(text='По дням недели', callback_data='days')
    income = InlineKeyboardButton(text='Справка', callback_data='income')
    if income_:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [income]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days]])
