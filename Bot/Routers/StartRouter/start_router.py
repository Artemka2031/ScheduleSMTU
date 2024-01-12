from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hcode
from ORM.create_database import GroupSchedule

startRouter = Router()


class Initialization(StatesGroup):
    user_id = State()
    chat_id = State()


@startRouter.message(CommandStart())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.set_state(Initialization.user_id)
    await message.answer(f"Здравствуй студент, {message.from_user.username}!")