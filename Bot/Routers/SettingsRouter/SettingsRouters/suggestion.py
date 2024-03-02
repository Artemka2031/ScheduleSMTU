from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from Bot.Keyboards.today_tomorrow_rep_kb import today_tomorrow_rep_keyboard
from Bot.Keyboards.reply_suggestion_inl_kb import reply_suggestion_kb, ReplyTypeCallback
from Bot.Middlewares import SuggestionLimitMiddleware
from Bot.Middlewares.admin_middleware import IsAdmMiddleware
from ORM.Tables.UserTables.suggestion_table import Suggestion

SuggestionRouter = Router()

# SuggestionRouter.message.middleware(IsRegMiddleware())
SuggestionRouter.message.middleware(SuggestionLimitMiddleware())


class SuggestionState(StatesGroup):
    user_id = State()
    messages_to_delete = State()
    sent_suggestion = State()
    reply_suggestion = State()
    suggestion_fill = State()


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

    if message.text[0] == '/':
        await state.clear()
        return

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


@SuggestionRouter.message(Command('suggestion_reply'))
async def reply_suggestion(message: Message, state: FSMContext):
    SuggestionRouter.message.middleware(IsAdmMiddleware())

    await state.clear()

    user_suggestion = Suggestion.get_user_suggestion()

    if user_suggestion:
        for user_id, suggestion in user_suggestion.items():
            await state.update_data(user_id=user_id, sent_suggestion=suggestion)
            await message.answer(f"Предложение от {user_id}: {suggestion}",
                                 reply_markup=reply_suggestion_kb())
    else:
        await message.answer(text="Предложений нет")


@SuggestionRouter.callback_query(ReplyTypeCallback.filter())
async def callback_to_kb(call: CallbackQuery, state: FSMContext, callback_data: ReplyTypeCallback) -> None:
    if callback_data.reply_type == "Ответить":
        await call.answer()
        await call.message.edit_text(text="Пришлите ответ на предложение")
        await state.set_state(SuggestionState.reply_suggestion)
    elif callback_data.reply_type == "Игнорировать":
        await call.answer()
        await call.message.delete()
        Suggestion.delete_suggestion((await state.get_data())["user_id"], (await state.get_data())["sent_suggestion"])
        await state.clear()


@SuggestionRouter.message(SuggestionState.reply_suggestion)
async def reply_suggestion(message: Message, state: FSMContext):
    reply_text = message.text

    await state.update_data(reply_suggestion=reply_text)

    if message.text[0] == '/':
        await state.clear()
        return

    try:
        await message.bot.send_message(chat_id=(await state.get_data())["user_id"], text=reply_text)
        await message.delete()
        Suggestion.delete_suggestion((await state.get_data())["user_id"], (await state.get_data())["sent_suggestion"])
    except Exception as e:
        print(e)

    await state.clear()
