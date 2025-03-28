from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize

def add_button_type(income_=False):
    interval = InlineKeyboardButton(text='Интервальный', callback_data='interval')
    days = InlineKeyboardButton(text='По дням недели', callback_data='days')
    income = InlineKeyboardButton(text=f'Справка' + emojize(':open_book:'), callback_data='income')
    if income_:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [income]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days]])


def add_button_days():
    mon = [InlineKeyboardButton(text='Пн', callback_data='day0')]
    tues = [InlineKeyboardButton(text='Вт', callback_data='day1')]
    wed = [InlineKeyboardButton(text='Ср', callback_data='day2')]
    thur = [InlineKeyboardButton(text='Чт', callback_data='day3')]
    frid = [InlineKeyboardButton(text='Пт', callback_data='day4')]
    sat = [InlineKeyboardButton(text='Сб', callback_data='day5')]
    sun = [InlineKeyboardButton(text='Вс', callback_data='day6')]
    end = [InlineKeyboardButton(text='Завершить', callback_data='dayend')]
    cancel = [InlineKeyboardButton(text='Отмена', callback_data='daycan')]

    return InlineKeyboardMarkup(inline_keyboard=[mon, tues, wed, thur, frid, sat, sun, end, cancel])
