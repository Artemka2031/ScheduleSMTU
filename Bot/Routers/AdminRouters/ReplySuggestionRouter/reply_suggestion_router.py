from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from Bot.Filters.not_comand_filter import isNotComandFilter
from Bot.Keyboards.reply_suggestion_inl_kb import reply_suggestion_kb, ReplyTypeCallback
from Bot.Middlewares.admin_middleware import IsAdmMiddleware
from Bot.RabbitMQProducer.producer_api import send_request_mq
from Bot.bot_initialization import moscow_tz


RepSuggestionRouter = Router()

RepSuggestionRouter.message.middleware(IsAdmMiddleware())


class SuggestionState(StatesGroup):
    sent_suggestion = State()
    reply_suggestion = State()
    suggestion_get = State()
    suggestion_fill = State()
    suggestion_id = State()


@RepSuggestionRouter.message(Command('suggestion_reply'))
async def reply_suggestion(message: Message, state: FSMContext):
    RepSuggestionRouter.message.middleware(IsAdmMiddleware())

    await state.clear()

    user_suggestion = await send_request_mq('bot.tasks.get_user_suggestion', [])

    await state.set_state(SuggestionState.suggestion_id)

    if user_suggestion:
        for user_id, inp_dictionary in user_suggestion.items():
            min_key = min(inp_dictionary, key=lambda x: x)
            suggestion = inp_dictionary[min_key]

            await state.update_data(user_id=user_id, sent_suggestion=suggestion, suggestion_id=min_key)
            await message.answer(f"Предложение от {user_id}: {suggestion}",
                                 reply_markup=reply_suggestion_kb())
            await state.set_state(SuggestionState.suggestion_get)
    else:
        await message.answer(text="Предложений нет")


@RepSuggestionRouter.callback_query(ReplyTypeCallback.filter(), SuggestionState.suggestion_get)
async def callback_to_kb(call: CallbackQuery, state: FSMContext, callback_data: ReplyTypeCallback) -> None:
    if callback_data.reply_type == "Ответить":
        await call.answer()
        await call.message.edit_text(text="Пришлите ответ на предложение")
        await state.set_state(SuggestionState.reply_suggestion)
    elif callback_data.reply_type == "Игнорировать":

        await call.answer()
        await call.message.delete()

        data = await state.get_data()

        save_admin_response = await send_request_mq('bot.tasks.process_admin_response', [data["user_id"], data["suggestion_id"], str(datetime.now(moscow_tz).date()),
            "Проигнорировано"])

        if save_admin_response != 'success':
            print('Возникла ошибка с записью в базу данных')
        await state.clear()


@RepSuggestionRouter.message(SuggestionState.reply_suggestion, isNotComandFilter())
async def reply_suggestion(message: Message, state: FSMContext):
    reply_text = message.text

    await state.update_data(reply_suggestion=reply_text)

    try:
        await message.bot.send_message(chat_id=(await state.get_data())["user_id"], text=reply_text)
        await message.delete()

        data = await state.get_data()

        reply = await send_request_mq("bot.tasks.process_admin_response", [data["user_id"], data["suggestion_id"], str(datetime.now(moscow_tz).date()), data["reply_suggestion"]])

        if reply != 'success':
            print('Возникла ошибка с записью ответа в бд')

    except Exception as e:
        print(e)

    await state.clear()
