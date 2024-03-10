from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CanselMenuCallback(CallbackData, prefix="CM"):
    cansel: bool


class MenuCallback(CallbackData, prefix="MN"):
    operation: str


def create_menu_kb(cansel: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Расписание", callback_data=MenuCallback(operation="schedule").pack())
    builder.button(text="Преподаватели", callback_data=MenuCallback(operation="teachers").pack())
    builder.button(text="Смена группы", callback_data=MenuCallback(operation="change_group").pack())

    builder.adjust(2)

    if cansel:
        builder.row(InlineKeyboardButton(text="Отмена", callback_data=CanselMenuCallback(cansel=True).pack()))

    return builder.as_markup()



