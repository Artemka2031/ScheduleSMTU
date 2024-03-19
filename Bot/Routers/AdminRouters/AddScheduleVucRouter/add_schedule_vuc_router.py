import os

from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.utils.markdown import hbold

from Bot.Keyboards.vuc_del_previous_schedule_inl_kb import vuc_del_previous_schedule_kb, PreviousVucCallback
from Bot.Keyboards.add_schedule_vuc_inl_kb import add_schedule_vuc_kb, TypeWeekVucCallback
from Bot.Middlewares.admin_middleware import IsAdmMiddleware
from Bot.Filters.not_comand_filter import isNotComandFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

AddScheduleVucRouter = Router()
AddScheduleVucRouter.message.middleware(IsAdmMiddleware())


class AddScheduleState(StatesGroup):
    type_week = State()
    schedule_downloaded = State()
    delete_state = State()
    this_week = State()


@AddScheduleVucRouter.message(Command("vuc"))
async def vuc_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(text="Выберите неделю, на которую хотите добавить расписание ВУЦ",
                         reply_markup=add_schedule_vuc_kb())
    await state.set_state(AddScheduleState.type_week)


@AddScheduleVucRouter.callback_query(AddScheduleState.type_week, TypeWeekVucCallback.filter())
async def this_week_schedule_request(call: CallbackQuery, state: FSMContext,
                                     callback_data: TypeWeekVucCallback) -> None:
    try:
        await call.bot.delete_messages(chat_id=call.message.chat.id, message_ids=[call.message.message_id])
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    if callback_data.week_type == "Эта неделя":
        await state.update_data(this_week=True)
        await call.message.answer(f'Пришлите фотографию с расписанием ВУЦ на {hbold("эту неделю")}')
    else:
        await state.update_data(this_week=False)
        await call.message.answer(f'Пришлите фотографию с расписанием ВУЦ на {hbold("следующую неделю")}')

    await state.set_state(AddScheduleState.schedule_downloaded)


@AddScheduleVucRouter.message(AddScheduleState.schedule_downloaded)
async def save_this_week_schedule(message: Message, state: FSMContext) -> None:
    try:
        await message.bot.delete_messages(chat_id=message.chat.id,
                                          message_ids=[message.message_id, message.message_id - 1])
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    directory = 'ORM/VUC/NewSchedule'
    os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует

    file_path = os.path.join(directory, 'new_file_ids.txt')

    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass

    this_week = (await state.get_data())["this_week"]

    with open(file_path, 'r+') as file:
        lines = file.readlines()

        if not lines:
            lines = ["\n", "\n"]

        if this_week:
            lines[0] = message.photo[-1].file_id + '\n'
        else:
            lines[1] = message.photo[-1].file_id + '\n'

        file.seek(0)
        file.writelines(lines[:2])
        file.truncate()
        file.close()

    await state.clear()
    await message.answer("Расписание успешно загружено\n\nЕсли вам вдруг необходимо удалить расписание соответствующей недели, нажмите на одну из кнопок ниже",
                         reply_markup=vuc_del_previous_schedule_kb())
    await state.set_state(AddScheduleState.delete_state)


@AddScheduleVucRouter.callback_query(AddScheduleState.delete_state, PreviousVucCallback.filter())
async def delete_previous_schedule(call: CallbackQuery, state: FSMContext, callback_data: PreviousVucCallback) -> None:
    try:
        await call.bot.delete_messages(chat_id=call.message.chat.id, message_ids=[call.message.message_id])
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    line_number = (0 if callback_data.previous_schedule == "Текущая неделя" else 1)

    file_path = 'ORM/VUC/NewSchedule/new_file_ids.txt'

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if lines:
            lines[line_number] = '\n'
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        file.close()
    await call.message.answer(text="Расписание успешно удалено")
    await state.clear()