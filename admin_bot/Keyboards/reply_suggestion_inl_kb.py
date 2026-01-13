from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ReplyTypeCallback(CallbackData, prefix="reply_ignore"):
    reply_type: str


def reply_suggestion_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Ответить", callback_data=ReplyTypeCallback(reply_type="Ответить").pack())
    builder.button(text="Игнорировать", callback_data=ReplyTypeCallback(reply_type="Игнорировать").pack())

    builder.adjust(2)

    return builder.as_markup()