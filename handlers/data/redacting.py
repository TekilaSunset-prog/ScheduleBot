import aiogram

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from emoji import emojize

from handlers.data.buttons import add_button_list, add_button_output, add_button_sure
from handlers.data.writing import ScheduleDb, UsersDb, REM

router_out = aiogram.Router()


# Редактирование данных пользователем
@router_out.message(Command('list'))
async def lists(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = ScheduleDb.get_data(f'user_id = {user_id}')
    sp = []
    for i in data:
        sp.append(i[1])
    await message.answer('Выберите заметку', reply_markup=add_button_list(sp))


@router_out.callback_query(lambda x: 'list' in x.data)
async def output(callback: aiogram.types.CallbackQuery):
    count = callback.data.replace("list", "")
    data = ScheduleDb.get_data(f'user_id = {callback.message.chat.id} and count = {count}',
                               select='type, days, time, text_, count, name', al=False)
    if data is None:
        await callback.message.edit_text('Этой заметки уже нет с нами')
    else:
        days = data[1]
        if days[len(days) - 1] == '0':
            one = 'Одноразовый'
            days = days.replace(':0', '')
        else:
            one = 'Многоразовый'
            days = days.replace(':1', '')

        if data[0] == 'days':
            type_ = 'По дням недели.'
            days_text = 'Дни недели:\n'
            form = {
                0: 'Понедельник',
                1: 'Вторник',
                2: 'Среда',
                3: 'Четверг',
                4: 'Пятница',
                5: 'Суббота',
                6: 'Воскресенье'
            }
            le = len(days)
            for i in range(le):
                if i + 1 == le:
                    days_text += f'{i + 1}. {form[int(days[i])]}'
                    continue
                days_text += f'{i + 1}. {form[int(days[i])]}\n'

        else:
            type_ = 'Интервальный.'
            days_text = f'Время между напоминаниями: {days} дней'

        await callback.message.edit_text(
            f'''
            Описание вашей {data[4] + 1} заметки под названием "{data[5]}":\n\n- Тип заметки: {type_} {one}\n- {days_text}\n- Время, в которое приходит напоминание: {data[2]}
            ''', reply_markup=add_button_output(data[4])
        )


@router_out.callback_query(lambda x: x.data == 'sp')
async def sp_(callback: aiogram.types.CallbackQuery):
    data = ScheduleDb.get_data(f'user_id = {callback.message.chat.id}')
    sp = []
    for i in data:
        sp.append(i[1])

    await callback.message.edit_text('Выберите заметку', reply_markup=add_button_list(sp))


@router_out.callback_query(lambda x: 'redact' in x.data)
async def redact(callback: aiogram.types.CallbackQuery):
    pass


@router_out.callback_query(lambda x: 'del' in x.data)
async def delete(callback: aiogram.types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Вы уверены?', reply_markup=add_button_sure(callback.data[3]))


@router_out.callback_query(lambda x: 'yes' in x.data or 'no' in x.data)
async def sure(callback: aiogram.types.CallbackQuery):
    await callback.message.delete()
    user_id = callback.message.chat.id
    if callback.data[:2:] == 'no':
        count = callback.data[2]
        await callback.message.answer('Отмена⛔', reply_markup=add_button_output(count, back_=True))
    else:
        count = callback.data[3]
        ScheduleDb.delete(f'user_id = {user_id} and count = {count}')

        data = ScheduleDb.get_data(f'user_id = {user_id} and count > {count}', select='count')
        if data:
            for element in data:
                ScheduleDb.update_db(f'count = {element[0] - 1}', f'user_id = {user_id} and count = {element[0]}')
                UsersDb.update_db(f'count = count - 1', f'user_id = {user_id}')
        else:
            UsersDb.update_db(f'count = count - 1', f'user_id = {user_id}')

        await callback.message.answer('Успешно✔️', reply_markup=add_button_output(count, back_=True))


@router_out.callback_query(lambda x: x.data == 'create')
async def create(callback: aiogram.types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    count = UsersDb.get_data(f'user_id = {user_id}', select='count', al=False)
    if count is None:
        count = -1
        UsersDb.add_data((user_id, count))
    else:
        count = count[0]
    await callback.message.delete()
    if count == 9:
        await callback.message.answer(f'Ошибка{emojize(":prohibited:")}. Максимальное количество заметок - 10')
    else:
        await callback.message.answer('Введите название заметки')
        await state.update_data(count=count + 1)
        await state.update_data(user_id=user_id)
        await state.set_state(REM.name)
