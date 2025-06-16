from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class EventTypeCallback(CallbackData, prefix="send_cancel_edit"):
    event_type: str


def mailing_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Отправить", callback_data=EventTypeCallback(event_type="Отправить").pack())
    builder.button(text="Редактировать", callback_data=EventTypeCallback(event_type="Редактировать").pack())
    builder.button(text="Отмена", callback_data=EventTypeCallback(event_type="Отмена").pack())

    builder.adjust(2)

    return builder.as_markup()