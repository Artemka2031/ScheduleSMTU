from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from Bot.Filters.check_group_number_filter import CheckGroupFilter, CheckCurrentGroupFilter
from Bot.Keyboards.change_current_group_kb import create_change_current_group_kb, ChangeCurrentGroupCallback
from Bot.Keyboards.today_tomorrow_rep_kb import today_tomorrow_rep_keyboard
from Bot.Middlewares import IsRegMiddleware
from ORM.users_info import User

ChangeGroupRouter = Router()


# ChangeGroupRouter.message.middleware(IsRegMiddleware())

class ChangeGroupState(StatesGroup):
    user_id = State()
    group_number = State()
    messages_to_delete = State()


@ChangeGroupRouter.message(Command("change_group"))
async def change_group_number(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(ChangeGroupState.user_id)
    sent_message = await message.answer(
        f"Ваша текущая группа {User.get_group_number(message.from_user.id)}.\nОставьте текущую или напишите новую:",
        reply_markup=create_change_current_group_kb())

    await state.update_data(messages_to_delete=[message.message_id, sent_message.message_id])
    await state.set_state(ChangeGroupState.group_number)


@ChangeGroupRouter.callback_query(ChangeCurrentGroupCallback.filter(F.change_group == False))
async def cancel_change_group(query: Message, state: FSMContext):
    user_id = query.from_user.id

    data = (await state.get_data())["messages_to_delete"]
    data.append(query.message.message_id)

    try:
        for message_id in data:
            await query.message.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    await query.message.answer(f"Выбрана группа {User.get_group_number(query.from_user.id)}",
                               reply_markup=today_tomorrow_rep_keyboard())
    await state.clear()


@ChangeGroupRouter.message(ChangeGroupState.group_number, CheckGroupFilter(), CheckCurrentGroupFilter())
async def set_group_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    group_number = int(message.text)

    User.change_group_number(user_id, group_number)

    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    try:
        for message_id in data:
            await message.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение пользователю
    await message.answer(f"Выбрана группа {group_number}",
                         reply_markup=today_tomorrow_rep_keyboard())


@ChangeGroupRouter.message(ChangeGroupState.group_number, ~CheckGroupFilter())
async def invalid_group_number(message: Message, state: FSMContext):
    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    sent_message = await message.answer(f"Такой группы не существует. Попробуйте еще раз:")
    data.append(sent_message.message_id)

    await state.update_data(messages_to_delete=data)
    await state.set_state(ChangeGroupState.group_number)


@ChangeGroupRouter.message(ChangeGroupState.group_number, ~CheckCurrentGroupFilter())
async def same_group_number(message: Message, state: FSMContext):
    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    sent_message = await message.answer(
        text=f"Группа {User.get_group_number(message.from_user.id)} уже выбрана.\nОставьте текущую или напишите новую:",
        reply_markup=create_change_current_group_kb())
    data.append(sent_message.message_id)
    await state.update_data(messages_to_delete=data)

    await state.set_state(ChangeGroupState.group_number)
