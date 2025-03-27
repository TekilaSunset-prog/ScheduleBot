import aiogram
from emoji import emojize

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.buttons import add_button_type, add_button_days
from DataBases.db import DB

router = aiogram.Router()
ScheduleDb = DB()
UsersDb = DB(table='users', count=2)

class REM(StatesGroup):
    time = State()
    days = State()
    text_ = State()
    type = State()
    count = State()


@router.message(Command('rem'))
async def remember(message: aiogram.types.Message, state: FSMContext):
    count = UsersDb.get_data(f'user_id = {message.from_user.id}', select='count')
    if not count:
        UsersDb.add_data((message.from_user.id, 1))
    if 10 in count:
        await message.answer(f'{emojize(":prohibited:")}Ошибка. Максимальное количество заметок - 10')
        UsersDb.add_data((message.from_user.id, max(count) + 1))
    else:
        await message.answer('Какой тип должен быть у напоминания?', reply_markup=add_button_type(True))
    await state.update_data(count=count+1)


@router.callback_query(lambda x: x.data == 'income')
async def income(callback: aiogram.types.CallbackQuery):
    await callback.message.edit_text('Интервальный - Напоминание будет приходить раз в то количество дней, сколько будет указано\n\nПо дням недели - Напоминание приходит в указанные дни недели', reply_markup=add_button_type())


@router.callback_query(lambda x: x.data == 'days')
async def days(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите дни в которых вам должно приходить напоминание', reply_markup=add_button_days())
    await state.update_data(type='days')


@router.callback_query(lambda x: 'day' in x.data)
async def days1(callback: aiogram.types.CallbackQuery, state: FSMContext):
    count = state.get_value('count')
    if callback.data == 'dayend':
        if not ScheduleDb.get_data(select='days', where=f'user_id = {callback.message.from_user.id}')[count - 1]:

            await callback.answer(f'{emojize(":cross_mark:")}Ошибка. Вы не добавили ни одного дня')

        else:
            await callback.message.delete()
            await callback.message.answer(
                f'{emojize(":check_mark:")}Успешно. Теперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM. Введите cancel, чтобы отменить создание заметки')
            await state.set_state(REM.time)



@router.callback_query(lambda x: x.data == 'interval')
async def interval(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите количество дней, которое должно проходить между напоминаниями. Введите cancel, чтобы отменить создание заметки')
    await state.set_state(REM.days)
    await state.update_data(type='interval')


@router.message(REM.days)
async def days(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(":no_entry:")}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        error = False
        try:
            if int(message.text) >= 365 or int(message.text) <= 0:
                await message.answer(f'{emojize(":cross_mark:")}Ошибка. Минимальное количество дней- 1, Максимальное - 364')
                error = True
        except ValueError:
            await message.answer(f'{emojize(":cross_mark:")}Ошибка. Вводите только число')
            error = True

        if not error:
            await state.update_data(days=message.text)
            await message.answer(f'{emojize(":check_mark:")}Успешно. Теперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM. Введите cancel, чтобы отменить создание заметки')
            await state.set_state(REM.time)


@router.message(REM.time)
async def time_(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(":no_entry:")}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        error = False
        err_text = f'{emojize(":cross_mark:")}Ошибка. Неправильный формат ввода'
        text = message.text

        try:
            if int(text[:2]) >= 24 or int(text[:2]) < 0:
                error = True
                await message.answer(err_text)
            else:
                if int(text[3:5]) >= 60 or int(text[3:5]) < 0:
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
                await message.answer(f'{emojize(":check_mark:")}Успешно. Теперь введите текст напоминания (макс. 5000 символов). Введите cancel, чтобы отменить создание заметки')
                await state.set_state(REM.text_)


@router.message(REM.text_, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def text_(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(":no_entry:")}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(":cross_mark:")}Ошибка')
        await state.clear()
    else:
        text = message.text
        if len(text) > 5000:
            await message.answer(f'{emojize(":cross_mark:")}Ошибка. Слишком много символов. Максимум 5000')
        else:
            await state.update_data(text_=text)
            data = await state.get_data()
            await state.clear()
            data.update({'type': 'interval'})
            ScheduleDb.add_data(tuple(data.values()))

            await message.answer(f'{emojize(":check_mark:")}Готово. Теперь вам будут приходить напоминания в нужное время')
