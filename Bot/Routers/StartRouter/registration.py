from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Filters.Check_group_number import CheckGroupFilter
from Bot.Keyboards.TT_kb import tt_kb
from ORM.Users_info import User

RegistrationRouter = Router()


class RegistrationState(StatesGroup):
    user_id = State()
    group_number = State()
    messages_to_delete = State()


@RegistrationRouter.message(Command("registration"))
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RegistrationState.user_id)

    sent_message = await message.answer(f"{hbold('Напиши номер совей группы и я смогу отправлять тебе расписание:')}")

    await state.update_data(user_id=message.from_user.id,
                            messages_to_delete=[sent_message.message_id, message.message_id])
    await state.set_state(RegistrationState.group_number)


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
                         reply_markup=tt_kb())


@RegistrationRouter.message(RegistrationState.group_number, ~CheckGroupFilter())
async def invalid_group_number(message: Message, state: FSMContext):
    await message.answer(f"Такой группы не существует. Попробуйте еще раз:")

    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    await state.update_data(messages_to_delete=data)
    await state.set_state(RegistrationState.group_number)
