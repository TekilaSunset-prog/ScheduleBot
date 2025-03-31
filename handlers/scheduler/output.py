import aiogram

from aiogram.filters import Command

from handlers.scheduler.buttons import add_button_list
from handlers.scheduler.writing import ScheduleDb

router_out = aiogram.Router()

@router_out.message(Command('list'))
async def lists(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = ScheduleDb.get_data(f'user_id = {user_id}')
    if not data:
        await message.answer('У вас ни одной заметки')
    else:
        sp = []
        for i in data:
            sp.append(i[1])
        await message.answer('Выберите заметку', reply_markup=add_button_list(sp))


@router_out.callback_query(lambda x: 'list' in x.data)
async def output(callback: aiogram.types.CallbackQuery):
    name = callback.data.replace("list", "")
    data = ScheduleDb.get_data(f'user_id = {callback.message.chat.id} and name = "{name}"', select='type, days, time, text_, count', al=False)
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
        Описание вашей {data[4]} заметки под названием "{name}":\n\n- Тип заметки: {type_} {one}\n- {days_text}\n- Время, в которое приходит напоминание: {data[2]}
        '''
    )


@router_out.callback_query(lambda x: x.data == 'sp')
async def sp_(callback: aiogram.types.CallbackQuery):
    data = ScheduleDb.get_data(f'user_id = {callback.message.chat.id}')
    sp = []
    for i in data:
        sp.append(i[1])
    await callback.message.edit_text('Выберите заметку', reply_markup=add_button_list(sp))