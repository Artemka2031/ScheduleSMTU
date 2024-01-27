from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from Bot.Filters.Check_group_number import CheckGroupFilter
from Bot.Keyboards.TT_kb import tt_kb
from ORM.Users_info import User

InitializationRouter = Router()


class Initialization(StatesGroup):
    user_id = State()
    group_number = State()


@InitializationRouter.message(CommandStart())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.set_state(Initialization.user_id)
    await state.update_data(user_id=message.from_user.id)
    await message.answer(
        f"Здравствуй студент {message.from_user.username}!"
        f" Напиши номер совей группы и я смогу отправлять тебе расписание:")
    await state.set_state(Initialization.group_number)


@InitializationRouter.message(Initialization.group_number, CheckGroupFilter())
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


@InitializationRouter.message(Initialization.group_number, ~CheckGroupFilter())
async def invalid_group_number(message: Message, state: FSMContext):
    await message.answer(f"Такой группы не существует. Попробуйте еще раз:")
    await state.set_state(Initialization.group_number)
