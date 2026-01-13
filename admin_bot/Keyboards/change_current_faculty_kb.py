from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ChangeCurrentFacultyCallback(CallbackData, prefix="CCF"):
    change_faculty_flag: bool


def create_change_current_faculty_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Оставить текущий", callback_data=ChangeCurrentFacultyCallback(change_faculty_flag=False).pack())
    builder.button(text="Выбрать другой", callback_data=ChangeCurrentFacultyCallback(change_faculty_flag=True).pack())
    builder.adjust(2)
    return builder.as_markup()

