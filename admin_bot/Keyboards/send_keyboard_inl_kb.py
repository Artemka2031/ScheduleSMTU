from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SendKbTypeCallback(CallbackData, prefix="send_keyboard"):
    send_kb_event: str


def send_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Отправить", callback_data=SendKbTypeCallback(send_kb_event="Отправить").pack())
    builder.button(text="Не отправлять", callback_data=SendKbTypeCallback(send_kb_event="Не отправлять").pack())

    builder.adjust(2)

    return builder.as_markup()