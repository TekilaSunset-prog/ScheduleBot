import aiogram
from emoji import emojize

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.buttons import add_button_type
from db.db_schedule import DB

router = aiogram.Router()
db = DB()


class REM(StatesGroup):
    time = State()
    days = State()
    text_ = State()


@router.message(Command('rem'))
async def remember(message: aiogram.types.Message):
    user = db.get_data(select='user_id', where=f'user_id like {message.from_user.id}')
    if len(user) == 0:
        count = 1
    else:
        last = user[len(user) - 1]
        count = last[len(last) - 1]
    if count == 10:
        await message.answer(f'{emojize(':prohibited:')}Ошибка. Максимальное количество заметок - 10')

    await message.answer('Какой тип должен быть у напоминания?', reply_markup=add_button_type(True))


@router.callback_query(lambda x: x.data == 'income')
async def income(callback: aiogram.types.CallbackQuery):
    await callback.message.edit_text('Интервальный - Напоминание будет приходить раз в то количество дней, сколько будет указано\n\nПо дням недели - Напоминание приходит в указанные дни недели', reply_markup=add_button_type())


@router.callback_query(lambda x: x.data == 'interval')
async def interval(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите количество дней, которое должно проходить между напоминаниями. Введите cancel, чтобы отменить создание заметки')
    await state.set_state(REM.days)


@router.message(REM.days)
async def days(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(':no_entry:')}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(':cross_mark:')}Ошибка')
        await state.clear()
    else:
        error = False
        try:
            if int(message.text) >= 365 or int(message.text) <= 0:
                await message.answer(f'{emojize(':cross_mark:')}Ошибка. Минимальное количество дней- 1, Максимальное - 364')
                error = True
        except ValueError:
            await message.answer(f'{emojize(':cross_mark:')}Ошибка. Вводите только число')
            error = True

        if not error:
            await state.update_data(days=message.text)
            await message.answer(f'{emojize(':check_mark:')}Успешно. Теперь введите время в которое вам должно приходить напоминание. Формат - ЧЧ:MM. Введите cancel, чтобы отменить создание заметки')
            await state.set_state(REM.time)


@router.message(REM.time)
async def time_(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(':no_entry:')}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(':cross_mark:')}Ошибка')
        await state.clear()
    else:
        error = False
        err_text = f'{emojize(':cross_mark:')}Ошибка. Неправильный формат ввода'
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
                await message.answer(f'{emojize(':check_mark:')}Успешно. Теперь введите текст напоминания (макс. 5000 символов). Введите cancel, чтобы отменить создание заметки')
                await state.set_state(REM.text_)


@router.message(REM.text_, aiogram.F.content_type == aiogram.types.ContentType.TEXT)
async def text_(message: aiogram.types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer(f'{emojize(':no_entry:')}Отмена')
        await state.clear()
    elif message.text[0] == '/':
        await message.answer(f'{emojize(':cross_mark:')}Ошибка')
        await state.clear()
    else:
        text = message.text
        if len(text) > 5000:
            await message.answer(f'{emojize(':cross_mark:')}Ошибка. Слишком много символов. Максимум 5000')
        else:
            await state.update_data(text_=text)
            data = await state.get_data()
            await state.clear()

            db.add_data(tuple(data.values()))

            await message.answer(f'{emojize(':check_mark:')}Готово. Теперь вам будут приходить напоминания в нужное время')
