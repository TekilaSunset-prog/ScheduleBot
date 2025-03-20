import sqlite3
import aiogram

from os.path import getsize
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.buttons import add_button_type

router = aiogram.Router()


class REM(StatesGroup):
    time = State()
    days = State()
    text = State()


@router.message(Command('rem'))
async def remember(message: aiogram.types.Message):
    await message.answer('Какой тип должен быть у напоминания?', reply_markup=add_button_type(True))


@router.callback_query(lambda x: x.data == 'income')
async def income(callback: aiogram.types.CallbackQuery):
    await callback.message.edit_text('Интервальный - Напоминание будет приходить раз в то количество дней, сколько будет указано\n\nПо дням недели - Напоминание приходит в указанные дни недели', reply_markup=add_button_type())


@router.callback_query(lambda x: x.data == 'interval')
async def interval(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите количество дней, которое должно проходить между напоминаниями')
    await state.set_state(REM.days)


@router.message(REM.days)
async def days(message: aiogram.types.Message, state: FSMContext):
    if message.text[0] == '/':
        await state.clear()
    error = False
    try:
        if int(message.text) >= 365:
            await message.answer('Максимальное количество дней - 364')
            error = True
    except ValueError:
        await message.answer('Вводите только число')
        error = True

    if not error:
        await state.update_data(days=message.text)
        await message.answer('Готово. Теперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM')
        await state.set_state(REM.time)


@router.message(REM.time)
async def time_(message: aiogram.types.Message, state: FSMContext):
    if message.text[0] == '/':
        await state.clear()
    error = False
    err_text = 'Неправильный формат ввода'
    text = message.text

    try:
        if int(text[:2]) >= 24 or int(text[:2]) < 0:
            error = True
            await message.answer(err_text)
        else:
            if int(text[3:5]) >= 24 or int(text[3:5]) < 0:
                error = True
                await message.answer(err_text)
    except ValueError:
        await message.answer(err_text)
        error = True

    if not error:
        if len(text) != 5:
            await message.answer(err_text)
        else:
            await state.update_data(time=text)
            await message.answer('Готово. Теперь введите текст напоминания (макс. 5000 символов)')
            await state.set_state(REM.text)


@router.message(REM.text, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def text_(message: aiogram.types.Message, state: FSMContext):
    text = message.text
    if len(text) > 5000:
        await message.answer('Слишком много символов. Максимум 5000')



