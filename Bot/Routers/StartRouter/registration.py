from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Filters.check_group_number_filter import CheckGroupFilter
from Bot.Filters.authentication_filter import isRegFilter
from Bot.Keyboards.today_tomorrow_rep_kb import today_tomorrow_rep_keyboard
from ORM.Tables.UserTables.user_table import User

RegistrationRouter = Router()


class RegistrationState(StatesGroup):
    user_id = State()
    group_number = State()
    messages_to_delete = State()


@RegistrationRouter.message(Command("registration"), ~isRegFilter())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RegistrationState.user_id)

    sent_message = await message.answer(f"{hbold('Напиши номер совей группы и я смогу отправлять тебе расписание:')}")

    await state.update_data(user_id=message.from_user.id,
                            messages_to_delete=[sent_message.message_id, message.message_id])
    await state.set_state(RegistrationState.group_number)


@RegistrationRouter.message(Command("registration"), isRegFilter())
async def already_registered(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f"Вы уже зарегистрированы. Ваша текущая группа: {User.get_group_number(message.from_user.id)}.\n\n"
             f"Чтобы изменить группу, напишите /change_group.",
        reply_markup=today_tomorrow_rep_keyboard())


@RegistrationRouter.message(RegistrationState.group_number, CheckGroupFilter())
async def set_group_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    group_number = int(message.text)

    try:
        User.registrate_user(user_id, group_number)
    except Exception as e:
        print(e)

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
    await message.answer(f"Выбрана группа {group_number}.",
                         reply_markup=today_tomorrow_rep_keyboard())


@RegistrationRouter.message(RegistrationState.group_number, ~CheckGroupFilter())
async def invalid_group_number(message: Message, state: FSMContext):
    await message.answer(f"Такой группы не существует. Попробуйте еще раз:")

    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    await state.update_data(messages_to_delete=data)
    await state.set_state(RegistrationState.group_number)
