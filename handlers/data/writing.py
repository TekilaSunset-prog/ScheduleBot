import aiogram
from emoji import emojize

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.data.buttons import add_button_type, add_button_days, add_button_cancel, add_button_one
from DataBases.db import DB

router_w = aiogram.Router()
ScheduleDb = DB()
UsersDb = DB(table='users', count=2)


# Запись в базу данных
class REM(StatesGroup):
    user_id = State()
    name = State()
    days = State()
    time = State()
    text_ = State()
    type = State()
    count = State()


@router_w.message(Command('create'))
async def create(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    count = UsersDb.get_data(f'user_id = {user_id}', select='count', al=False)
    if count is None:
        count = -1
        UsersDb.add_data((user_id, count))
    else:
        count = count[0]

    if count == 9:
        await message.answer(f'Ошибка{emojize(":prohibited:")}. Максимальное количество заметок - 10')
    else:
        await message.answer('Введите название заметки')
        await state.update_data(count=count + 1)
        await state.update_data(user_id=user_id)
        await state.set_state(REM.name)


@router_w.message(REM.name, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def name(message: aiogram.types.Message, state: FSMContext):
    count = await state.get_value('count')
    if message.text[0] == '/':
        await message.answer(f'Ошибка{emojize(":cross_mark:")}')
        await state.clear()
    else:
        await state.update_data(name=message.text)
        await state.set_state()
        await message.answer(f'Успешно{emojize(":check_mark:")}.\nКакого типа должна быть заметка?', reply_markup=add_button_type(count, True))


@router_w.callback_query(lambda x: x.data == 'income')
async def income(callback: aiogram.types.CallbackQuery, state: FSMContext):
    count = await state.get_value('count')
    await callback.message.edit_text(
        'Интервальная - Напоминание будет приходить раз в то количество дней, сколько будет указано\n\nПо дням недели - Напоминание приходит в указанные дни недели',
        reply_markup=add_button_type(count))


@router_w.callback_query(lambda x: x.data == 'days')
async def days1(callback: aiogram.types.CallbackQuery, state: FSMContext):
    count = await state.get_value('count')
    await callback.message.answer('Выберите дни в которых вам должно приходить напоминание и нажмите на кнопку "завершить"',
                                  reply_markup=add_button_days(count))
    await callback.message.delete()
    await state.update_data(type='days')


@router_w.callback_query(lambda x: 'day' in x.data)
async def days2(callback: aiogram.types.CallbackQuery, state: FSMContext):
    days = await state.get_value('days')
    count = await state.get_value('count')
    if days is None:
        days = ''

    if callback.data == 'dayend':
        if days == '':
            await callback.answer(f'Ошибка{emojize(":cross_mark:")}. Вы не добавили ни одного дня')
        else:
            await callback.message.delete()
            await callback.message.answer(
                f'Успешно{emojize(":check_mark:")}.\nТеперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n',
                reply_markup=add_button_cancel(count))
            await state.set_state(REM.time)
    else:
        day = callback.data.replace('day', '')
        if day not in days:
            days += day
            await callback.answer(f'Успешно{emojize(":check_mark:")}')
            await state.update_data(days=days)
        elif day in days:
            await callback.answer(f'{emojize(":cross_mark:")}Ошибка. Этот день уже добавлен')
        if len(days) == 7:
            await callback.message.delete()
            await callback.message.answer(
                f'Успешно{emojize(":check_mark:")}.\nТеперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n',
                reply_markup=add_button_cancel(count))
            await state.set_state(REM.time)


@router_w.callback_query(lambda x: x.data == 'interval')
async def interval(callback: aiogram.types.CallbackQuery, state: FSMContext):
    count = await state.get_value('count')
    await callback.message.answer('Введите количество дней, которое должно проходить между напоминаниями.\n',
                                  reply_markup=add_button_cancel(count))
    await callback.message.delete()
    await state.set_state(REM.days)
    await state.update_data(type='interval')


@router_w.message(REM.days)
async def days3(message: aiogram.types.Message, state: FSMContext):
    count = await state.get_value('count')
    if message.text[0] == '/':
        await message.answer(f'Ошибка{emojize(":cross_mark:")}')
        await state.clear()
    else:
        error = False
        try:
            if int(message.text) >= 365 or int(message.text) <= 0:
                await message.answer(
                    f'Ошибка{emojize(":cross_mark:")}. Минимальное количество дней- 1, Максимальное - 364',
                    reply_markup=add_button_cancel(count))
                error = True
        except ValueError:
            await message.answer(f'Ошибка{emojize(":cross_mark:")}. Вводите только число',
                                 reply_markup=add_button_cancel(count))
            error = True

        if not error:
            await state.update_data(days=message.text)
            await message.answer(
                f'Успешно{emojize(":check_mark:")}.\nТеперь введите время (по МСК) в которое вам должно приходить напоминание. Формат - ЧЧ:MM.\n',
                reply_markup=add_button_cancel(count))
            await state.set_state(REM.time)


@router_w.message(REM.time)
async def time_(message: aiogram.types.Message, state: FSMContext):
    count = await state.get_value('count')
    if message.text[0] == '/':
        await message.answer(f'Ошибка{emojize(":cross_mark:")}')
        await state.clear()
    else:
        error = False
        err_text = f'Ошибка{emojize(":cross_mark:")}. Неправильный формат ввода'
        text = message.text

        try:
            if int(text[:2]) >= 24 or int(text[:2]) < 0:
                error = True
                await message.answer(err_text, reply_markup=add_button_cancel(count))
            else:
                if int(text[3:5]) >= 60 or int(text[3:5]) < 0:
                    error = True
                    await message.answer(err_text, reply_markup=add_button_cancel(count))
        except ValueError:
            await message.answer(err_text, reply_markup=add_button_cancel(count))
            error = True

        if not error:
            if len(text) != 5:
                await message.answer(err_text, reply_markup=add_button_cancel(count))
            else:
                await state.set_state()
                await state.update_data(time=text)
                await message.answer(f'Успешно{emojize(":check_mark:")}.\nКакой должна быть заметка?', reply_markup=add_button_one(count))


@router_w.callback_query(lambda x: 'one' in x.data)
async def one(callback: aiogram.types.CallbackQuery, state: FSMContext):
    days = await state.get_value('days')
    type_ = await state.get_value('type')
    count = await state.get_value('count')

    if callback.data[3::] == ':0' and type_ == 'days' and len(days) > 1:
        await callback.message.delete()
        await callback.message.answer(f'Ошибка{emojize(":cross_mark:")}.\nУ одноразовой заметки не может быть несколько дней недели.', reply_markup=add_button_one(count))
    else:
        days += callback.data.replace('one', '')
        await state.update_data(days=days)
        await callback.message.delete()
        await callback.message.answer(
            f'Успешно{emojize(":check_mark:")}.\nТеперь введите текст напоминания (макс. 5000 символов).\n',
            reply_markup=add_button_cancel(count))
        await state.set_state(REM.text_)


@router_w.message(REM.text_, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def text_(message: aiogram.types.Message, state: FSMContext):
    count = await state.get_value('count')
    if message.text[0] == '/':
        await message.answer(f'Ошибка{emojize(":cross_mark:")}')
        await state.clear()
    else:
        text = message.text
        if len(text) > 5000:
            await message.answer(f'Ошибка{emojize(":cross_mark:")}. Слишком много символов. Максимум 5000',
                                 reply_markup=add_button_cancel(count))
        else:
            await state.update_data(text_=text)
            data = await state.get_data()
            count = await state.get_value('count')
            await state.clear()

            ScheduleDb.add_data(tuple(data.values()), queue=tuple(data.keys()))
            UsersDb.update_db(f'count = {count}', f'user_id = {message.from_user.id}')

            await message.answer(
                f'Готово{emojize(":check_mark:")}. Теперь вам будут приходить напоминания в нужное время')


@router_w.callback_query(lambda x: 'cancel' in x.data)
async def cancel(callback: aiogram.types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data or str(data.get('count')) != callback.data[6]:
        await callback.message.edit_text('Заметка уже создана /list')
    else:
        await callback.message.edit_text('Создание заметки отменено⛔')
        await state.clear()
