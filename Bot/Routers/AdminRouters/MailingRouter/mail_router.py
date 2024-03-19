from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command

from Bot.Keyboards.mailing_kb import mailing_kb, EventTypeCallback
from Bot.Middlewares.admin_middleware import IsAdmMiddleware
from Bot.Filters.not_comand_filter import isNotComandFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ORM.Tables.UserTables.user_table import User
from Bot.bot_initialization import setup_bot_commands
from Bot.Keyboards.send_keyboard_inl_kb import send_kb, SendKbTypeCallback
from Bot.Keyboards.today_tomorrow_rep_kb import today_tomorrow_rep_keyboard

MailRouter = Router()
MailRouter.message.middleware(IsAdmMiddleware())


class MailingState(StatesGroup):
    mail_data = State()
    editing_in_progress = State()
    send_edit_cancel_mailing_text = State()
    send_kb_to_users = State()


@MailRouter.message(Command("mailing"))
async def request_mail(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(text="Следующим сообщение введите содержание расслыки ✉️")
    await state.set_state(MailingState.mail_data)


@MailRouter.message(MailingState.mail_data, isNotComandFilter())
async def save_mailing_text(message: Message, state: FSMContext) -> None:
    await state.clear()

    try:
        await message.bot.delete_messages(chat_id=message.chat.id,
                                          message_ids=[message.message_id - 1, message.message_id - 2])
    except Exception:
        print(f"Ошибка при удалении сообщения: {Exception}")

    mailing_text = message.text
    await state.update_data(mail_data=mailing_text)
    await message.answer(
        f"Вы уверены, что хотите отправить следующее сообщение?\n\n{mailing_text}",
        reply_markup=mailing_kb())
    await state.set_state(MailingState.send_edit_cancel_mailing_text)


@MailRouter.callback_query(EventTypeCallback.filter(F.event_type == "Отмена"),
                           MailingState.send_edit_cancel_mailing_text)
async def cancel_mailing_text(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    try:
        await call.message.bot.delete_messages(chat_id=call.message.chat.id,
                                               message_ids=[call.message.message_id, call.message.message_id - 1])
    except Exception:
        print(f"Ошибка при удалении сообщения: {Exception}")
    await state.clear()


@MailRouter.callback_query(EventTypeCallback.filter(F.event_type == "Отправить"))
async def send_mailing_text(call: CallbackQuery, state: FSMContext) -> None:
    try:
        await call.message.bot.delete_messages(
            chat_id=call.message.chat.id,
            message_ids=[call.message.message_id, call.message.message_id - 1])
        await call.message.answer(
            text="Если вы хотите отправить новую клавиатуру пользователям, нажмите соответствующую кнопку 👇🏻",
            reply_markup=send_kb())
        await state.set_state(MailingState.send_kb_to_users)

    except Exception as e:
        print(f"Возникла ошибка: {e}")


@MailRouter.callback_query(EventTypeCallback.filter(F.event_type == "Редактировать"))
async def edit_mailing_text(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.answer()
    await call.message.edit_text(text="Пришлите исправленное сообщение с рассылкой")
    await state.set_state(MailingState.editing_in_progress)


@MailRouter.message(MailingState.editing_in_progress, isNotComandFilter())
async def edit_message(message: Message, state: FSMContext) -> None:
    await save_mailing_text(message, state)


@MailRouter.callback_query(SendKbTypeCallback.filter(), MailingState.send_kb_to_users)
async def send_kb_and_text_mailing(call: CallbackQuery, state: FSMContext, callback_data: SendKbTypeCallback) -> None:
    mailing_text = (await state.get_data())['mail_data']
    try:
        for user_id in User.get_all_users_ids():
            if callback_data.send_kb_event == "Отправить":
                await call.message.bot.send_message(chat_id=user_id,
                                                    text=mailing_text,
                                                    reply_markup=today_tomorrow_rep_keyboard())
                await setup_bot_commands(status="user", user_id=user_id)
            else:
                await call.message.bot.send_message(chat_id=user_id, text=mailing_text)

        await call.message.bot.delete_messages(
            chat_id=call.message.chat.id,
            message_ids=[call.message.message_id])
    except Exception as e:
        print(f"Возникла ошибка: {e}")

    await state.clear()
