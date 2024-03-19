from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PreviousVucCallback(CallbackData, prefix="previous_schedule"):
    previous_schedule: str


def vuc_del_previous_schedule_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Текущая неделя", callback_data=PreviousVucCallback(previous_schedule="Текущая неделя").pack())
    builder.button(text="Следующая неделя", callback_data=PreviousVucCallback(previous_schedule="Следующая неделя").pack())

    builder.adjust(2)

    return builder.as_markup()