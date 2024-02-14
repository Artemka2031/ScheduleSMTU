from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from Bot.Keyboards.today_tomorrow_rep_kb import today_tomorrow_rep_keyboard
from Bot.Middlewares import IsRegMiddleware, SuggestionLimitMiddleware
from ORM.users_info import Suggestion

SuggestionRouter = Router()

# SuggestionRouter.message.middleware(IsRegMiddleware())
SuggestionRouter.message.middleware(SuggestionLimitMiddleware())


class SuggestionState(StatesGroup):
    user_id = State()
    messages_to_delete = State()
    sent_suggestion = State()


@SuggestionRouter.message(Command('suggestion'))
async def send_suggestion(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(SuggestionState.user_id)

    sent_message = await message.answer("Команда разработчиков будет рада твоим пожеланиям:")
    await state.update_data(user_id=message.from_user.id,
                            messages_to_delete=[message.message_id, sent_message.message_id])
    await state.set_state(SuggestionState.sent_suggestion)


@SuggestionRouter.message(SuggestionState.sent_suggestion)
async def sent_suggestion(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = (await state.get_data())["messages_to_delete"]
    data.append(message.message_id)

    suggestion = message.text

    try:
        Suggestion.add_suggestion(user_id, suggestion)
    except Exception as e:
        print(e)

    try:
        for message_id in data:
            await message.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    await message.answer(f"Спасибо за пожелание: {suggestion}", reply_markup=today_tomorrow_rep_keyboard())
    await state.clear()
