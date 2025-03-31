from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize


def add_button_one():
    one = [InlineKeyboardButton(text='Одноразовая', callback_data='one:0')]
    many = [InlineKeyboardButton(text='Многоразовая', callback_data='one:1')]
    return InlineKeyboardMarkup(inline_keyboard=[one, many])


def add_button_type(income_=False):
    interval = InlineKeyboardButton(text='Интервальная', callback_data='interval')
    days = InlineKeyboardButton(text='По дням недели', callback_data='days')
    income = InlineKeyboardButton(text=f'Справка' + emojize(':open_book:'), callback_data='income')
    if income_:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [income], [InlineKeyboardButton(text='Отмена⛔', callback_data='cancel')]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [InlineKeyboardButton(text='Отмена⛔', callback_data='cancel')]])


def add_button_days():
    mon = [InlineKeyboardButton(text='Пн', callback_data='day0')]
    tues = [InlineKeyboardButton(text='Вт', callback_data='day1')]
    wed = [InlineKeyboardButton(text='Ср', callback_data='day2')]
    thur = [InlineKeyboardButton(text='Чт', callback_data='day3')]
    frid = [InlineKeyboardButton(text='Пт', callback_data='day4')]
    sat = [InlineKeyboardButton(text='Сб', callback_data='day5')]
    sun = [InlineKeyboardButton(text='Вс', callback_data='day6')]
    end = [InlineKeyboardButton(text='Завершить', callback_data='dayend')]
    cancel = [InlineKeyboardButton(text='Отмена⛔', callback_data='cancel')]

    return InlineKeyboardMarkup(inline_keyboard=[mon, tues, wed, thur, frid, sat, sun, end, cancel])


def add_button_cancel():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена⛔', callback_data='cancel')]])


def add_button_list(data):
    sp = []

    for i in data:
        sp.append(InlineKeyboardButton(text=i, callback_data=f'list{i}'))

    return InlineKeyboardMarkup(inline_keyboard=[sp])