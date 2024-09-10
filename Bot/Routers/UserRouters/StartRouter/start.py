from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Routers.UserRouters.StartRouter.registration import RegistrationState

StartRouter = Router()


@StartRouter.message(CommandStart())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привет, дружище! 👋\n\n"
        "Мы рады видеть тебя здесь! 😊 Этот бот создан, чтобы тебе было проще ориентироваться в учебной жизни нашего универа.\n\n"
        "👉 Смотри своё расписание на текущую неделю, планируй своё время на будущее — выбирай любую неделю или конкретный день 📅 через виджет календаря!\n\n"
        "👩‍🏫👨‍🏫 Хочешь узнать расписание своих преподавателей? Нажми 'Расписание' -> 'Твои преподаватели'. Или введи имя нужного препода, и мы найдём его расписание! 🔍\n\n"
        "🔄 Хочешь узнать расписание друзей? Используй команду /change_group, чтобы всегда быть в курсе актуальных занятий.\n\n"
        "💬 Есть идеи или пожелания? Напиши нам через команду /suggestion — мы всегда рады твоим предложениям!\n\n"
        "🔔 Хочешь быть в курсе актуального расписания каждый день? Включи уведомления о расписании командой /notification.\n\n"
        "Мы сами студенты и знаем, как важно держать всё под контролем, чтобы всё было чётко и круто! Так что пользуйся ботом, планируй своё время и будь на волне! 🚀"
    )

    sent_message = await message.answer(f"{hbold('Напиши номер совей группы и я смогу отправлять тебе расписание:')}")

    await state.set_state(RegistrationState.user_id)
    await state.update_data(user_id=message.from_user.id, messages_to_delete=[sent_message.message_id])
    await state.set_state(RegistrationState.group_number)
