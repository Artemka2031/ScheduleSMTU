from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from Bot.Keyboards.TT_kb import tt_kb
from ORM.Users_info import User

ChangeGroupRouter = Router()


class ChangeGroupState(StatesGroup):
    user_id = State()
    group_number = State()


@ChangeGroupRouter.message(Command("/change_group"))
async def change_group_number(message: Message, state: FSMContext):
    await state.set_state(ChangeGroupState.user_id)
    await message.answer(f"Напишите новый номер группы:")


@ChangeGroupRouter.message(ChangeGroupState.group_number)
async def set_group_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    group_number = int(message.text)
    # Проверяем, существует ли уже пользователь
    existing_user = User.get_user(user_id)

    if existing_user:
        # Если пользователь существует, обновляем номер группы
        User.change_group_number(user_id, group_number)
    else:
        # Если пользователь не существует, регистрируем нового пользователя
        User.registrate_user(user_id, group_number)

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение пользователю
    await message.answer(f"У вас успешно выбрана группа {group_number}. Теперь вы можете посмотреть расписание.",
                         reply_markup=tt_kb())
