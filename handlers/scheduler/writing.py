import aiogram
from emoji import emojize

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.scheduler.buttons import add_button_type, add_button_days, add_button_cancel
from DataBases.db import DB

router = aiogram.Router()
ScheduleDb = DB()
UsersDb = DB(table='users', count=2)

class REM(StatesGroup):
    user_id = State()
    days = State()
    time = State()
    text_ = State()
    type = State()
    count = State()


@router.message(Command('rem'))
async def remember(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    count = UsersDb.get_data(f'user_id = {user_id}', select='count', al=False)
    if count is None:
        count = 0
        UsersDb.add_data((user_id, count))
    else:
        count = count[0]

    if count == 10:
        await message.answer(f'{emojize(":prohibited:")}Ошибка. Максимальное количество заметок - 10')
    else:
        await message.answer('Какой тип должен быть у напоминания?', reply_markup=add_button_type(True))
        await state.update_data(count=count + 1)
        await state.update_data(user_id=user_id)


@router.callback_query(lambda x: x.data == 'income')
async def income(callback: aiogram.types.CallbackQuery):
    await callback.message.edit_text('Интервальный - Напоминание будет приходить раз в то количество дней, сколько будет указано\n\nПо дням недели - Напоминание приходит в указанные дни недели', reply_markup=add_button_type())


@router.callback_query(lambda x: x.data == 'days')
async def days1(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите дни в которых вам должно приходить напоминание', reply_markup=add_button_days())
    await callback.message.delete()
    await state.update_data(type='days')


@router.callback_query(lambda x: 'day' in x.data)
async def days2(callback: aiogram.types.CallbackQuery, state: FSMContext):
    days = await state.get_value('days')
    if days is None:
        days = ''

    if callback.data == 'dayend':
        if days == '':
            await callback.answer(f'{emojize(":cross_mark:")}Ошибка. Вы не добавили ни одного дня')
        else:
            await callback.message.delete()
            await callback.message.answer(
                f'{emojize(":check_mark:")}Успешно.\nТеперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n', reply_markup=add_button_cancel())
            await state.set_state(REM.time)
    else:
        day = callback.data.replace('day', '')
        if day not in days:
            days += day
            await callback.answer(f'{emojize(":check_mark:")}Успешно')
            await state.update_data(days=days)
        elif day in days:
            await callback.answer(f'{emojize(":cross_mark:")}Ошибка. Этот день уже добавлен')
        if len(days) == 7:
            await callback.message.delete()
            await callback.message.answer(
                f'{emojize(":check_mark:")}Успешно.\nТеперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n', reply_markup=add_button_cancel())
            await state.set_state(REM.time)


@router.callback_query(lambda x: x.data == 'interval')
async def interval(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите количество дней, которое должно проходить между напоминаниями.\n', reply_markup=add_button_cancel())
    await callback.message.delete()
    await state.set_state(REM.days)
    await state.update_data(type='interval')


@router.message(REM.days)
async def days3(message: aiogram.types.Message, state: FSMContext):
    if message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        error = False
        try:
            if int(message.text) >= 365 or int(message.text) <= 0:
                await message.answer(f'{emojize(":cross_mark:")}Ошибка. Минимальное количество дней- 1, Максимальное - 364', reply_markup=add_button_cancel())
                error = True
        except ValueError:
            await message.answer(f'{emojize(":cross_mark:")}Ошибка. Вводите только число', reply_markup=add_button_cancel())
            error = True

        if not error:
            await state.update_data(days=message.text)
            await message.answer(f'{emojize(":check_mark:")}Успешно.\nТеперь введите время (по МСК) в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n', reply_markup=add_button_cancel())
            await state.set_state(REM.time)


@router.message(REM.time)
async def time_(message: aiogram.types.Message, state: FSMContext):
    if message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        error = False
        err_text = f'{emojize(":cross_mark:")}Ошибка. Неправильный формат ввода'
        text = message.text

        try:
            if int(text[:2]) >= 24 or int(text[:2]) < 0:
                error = True
                await message.answer(err_text, reply_markup=add_button_cancel())
            else:
                if int(text[3:5]) >= 60 or int(text[3:5]) < 0:
                    error = True
                    await message.answer(err_text, reply_markup=add_button_cancel())
        except ValueError:
            await message.answer(err_text, reply_markup=add_button_cancel())
            error = True

        if not error:
            if len(text) != 5:
                await message.answer(err_text, reply_markup=add_button_cancel())
            else:
                await state.update_data(time=text)
                await message.answer(f'{emojize(":check_mark:")}Успешно.\nТеперь введите текст напоминания (макс. 5000 символов).\n', reply_markup=add_button_cancel())
                await state.set_state(REM.text_)


@router.message(REM.text_, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def text_(message: aiogram.types.Message, state: FSMContext):
    if message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        text = message.text
        if len(text) > 5000:
            await message.answer(f'{emojize(":cross_mark:")}Ошибка. Слишком много символов. Максимум 5000', reply_markup=add_button_cancel())
        else:
            await state.update_data(text_=text)
            data = await state.get_data()
            count = await state.get_value('count')
            await state.clear()

            UsersDb.update_db(f'count = {count}', f'user_id = {message.from_user.id}')
            ScheduleDb.add_data(tuple(data.values()), queue=tuple(data.keys()))

            await message.answer(f'{emojize(":check_mark:")}Готово. Теперь вам будут приходить напоминания в нужное время')


@router.callback_query(lambda x: x.data == 'cancel')
async def cancel(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('⛔Создание заметки отменено')
    await state.clear()
