from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize


def add_button_one(count):
    one = [InlineKeyboardButton(text='Одноразовая', callback_data='one:0')]
    many = [InlineKeyboardButton(text='Многоразовая', callback_data='one:1')]

    return InlineKeyboardMarkup(inline_keyboard=[one, many, [InlineKeyboardButton(text='Отмена⛔', callback_data=f'cancel{count}')]])


def add_button_type(count, income_=False):
    interval = InlineKeyboardButton(text='Интервальная', callback_data='interval')
    days = InlineKeyboardButton(text='По дням недели', callback_data='days')
    income = InlineKeyboardButton(text=f'Справка' + emojize(':open_book:'), callback_data='income')
    if income_:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [income], [InlineKeyboardButton(text='Отмена⛔', callback_data=f'cancel{count}')]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[interval], [days], [InlineKeyboardButton(text='Отмена⛔', callback_data=f'cancel{count}')]])


def add_button_days(count):
    mon = [InlineKeyboardButton(text='Пн', callback_data='day0')]
    tues = [InlineKeyboardButton(text='Вт', callback_data='day1')]
    wed = [InlineKeyboardButton(text='Ср', callback_data='day2')]
    thur = [InlineKeyboardButton(text='Чт', callback_data='day3')]
    frid = [InlineKeyboardButton(text='Пт', callback_data='day4')]
    sat = [InlineKeyboardButton(text='Сб', callback_data='day5')]
    sun = [InlineKeyboardButton(text='Вс', callback_data='day6')]
    end = [InlineKeyboardButton(text='Завершить', callback_data='dayend')]
    cancel = [InlineKeyboardButton(text='Отмена⛔', callback_data=f'cancel{count}')]

    return InlineKeyboardMarkup(inline_keyboard=[mon, tues, wed, thur, frid, sat, sun, end, cancel])


def add_button_cancel(count, red=''):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена⛔', callback_data=f'cancel{red}{count}')]])


def add_button_list(data):
    if not data:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f'Заметки кончились{emojize(":loudly_crying_face:")}', callback_data='create')]])
    sp = []

    for i in range(len(data)):
        sp.append([InlineKeyboardButton(text=data[i], callback_data=f'list{i}')])
    return InlineKeyboardMarkup(inline_keyboard=sp)


def add_button_output(count, back_=False):
    back = InlineKeyboardButton(text='<<Вернуться к списку заметок', callback_data='sp')
    if back_:
        return InlineKeyboardMarkup(inline_keyboard=[[back]])

    redact = InlineKeyboardButton(text='Изменить параметры заметки>>', callback_data=f'redact{count}')
    delete = InlineKeyboardButton(text='Удалить заметку', callback_data=f'del{count}')
    return InlineKeyboardMarkup(inline_keyboard=[[redact], [back], [delete]])


def add_button_sure(count):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=emojize(":check_mark:"), callback_data=f'yes{count}')], [InlineKeyboardButton(text=emojize(":cross_mark:"), callback_data=f'no{count}')]])


def add_button_redact(data, count):
    name = InlineKeyboardButton(text='Отредактировать название', callback_data=f'name{data[0] + count}')
    days = InlineKeyboardButton(text='Изменить дни', callback_data=f'days{data[1] + count}')
    time = InlineKeyboardButton(text='Изменить время', callback_data=f'time{data[2] + count}')
    type_ = InlineKeyboardButton(text='Поменять тип', callback_data=f'type{data[3] + count}')
    text = InlineKeyboardButton(text='Изменить текст', callback_data=f'text{data[4] + count}')
    back = InlineKeyboardButton(text='<<Вернуться к описанию', callback_data=f'back{count}')

    return InlineKeyboardMarkup(inline_keyboard=[[name], [days], [time], [type_], [text], [back]])
