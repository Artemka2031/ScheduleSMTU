from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ChangeCurrentGroupCallback(CallbackData, prefix="CCG"):
    change_group: bool


def create_change_current_group_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Оставить текущую", callback_data=ChangeCurrentGroupCallback(change_group=False).pack())
    return builder.as_markup()

