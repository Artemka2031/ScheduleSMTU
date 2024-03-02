from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command

from Bot.Keyboards.mailing_kb import mailing_kb, EventTypeCallback
from Bot.Middlewares.admin_middleware import IsAdmMiddleware

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ORM.Tables.UserTables.user_table import User

MailRouter = Router()
MailRouter.message.middleware(IsAdmMiddleware())


class MailingState(StatesGroup):
    mail_data = State()
    editing_in_progress = State()


@MailRouter.message(Command("mailing"))
async def request_mail(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(text="Следующим сообщение введите содержание расслыки ✉️")
    await state.set_state(MailingState.mail_data)


@MailRouter.message(MailingState.mail_data)
async def save_mailing_text(message: Message, state: FSMContext) -> None:
    await state.clear()

    if message.text[0] == '/':
        await state.clear()
        return

    try:
        await message.bot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id - 1])
    except Exception:
        print(f"Ошибка при удалении сообщения: {Exception}")

    mailing_text = message.text
    await state.update_data(mail_data=mailing_text)
    await message.answer(
        f"Вы уверены, что хотите отправить следующее сообщение?\n\n{mailing_text}",
        reply_markup=mailing_kb())


@MailRouter.callback_query(EventTypeCallback.filter())
async def mailing_type_event(call: CallbackQuery, state: FSMContext, callback_data: EventTypeCallback) -> None:
    if callback_data.event_type == "Отмена":
        await call.answer()
        try:
            await call.message.bot.delete_messages(chat_id=call.message.chat.id,
                                                   message_ids=[call.message.message_id, call.message.message_id - 1])
        except Exception:
            print(f"Ошибка при удалении сообщения: {Exception}")
        await state.clear()

    elif callback_data.event_type == "Отправить":
        await call.answer()
        mailing_text = (await state.get_data())['mail_data']
        try:
            for user_id in User.get_all_users_ids():
                await call.message.bot.send_message(chat_id=user_id, text=mailing_text)
            await call.message.delete()
        except Exception:
            print(f"Возникла ошибка: {Exception}")
        await state.clear()

    elif callback_data.event_type == "Редактировать":
        await state.clear()
        await call.answer()
        await call.message.edit_text(text="Пришлите исправленное сообщение с рассылкой")
        await state.set_state(MailingState.editing_in_progress)


@MailRouter.message(MailingState.editing_in_progress)
async def edit_message(message: Message, state: FSMContext) -> None:
    if message.text[0] == '/':
        await state.clear()
        return
    new_mailing_text = message.text
    await state.update_data(mail_data=new_mailing_text)
    await message.answer(text=f"Вы уверены, что хотите отправить следующее сообщение?\n\n{new_mailing_text}",
                         reply_markup=mailing_kb())

    try:
        await message.bot.delete_messages(chat_id=message.chat.id,
                                          message_ids=[message.message_id - 2, message.message_id - 1])
    except Exception:
        print(f"Ошибка при удалении сообщения: {Exception}")
