from typing import List, Dict

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class TeacherTextCallback(CallbackData, prefix="TTC"):
    teacher: int | str

def create_choose_teachers_kb(teachers: List[Dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for teacher in teachers:
        last_name = teacher["last_name"]
        first_name = teacher["first_name"]
        middle_name = teacher["middle_name"]
        teacher_id = teacher["id"]

        callback = TeacherTextCallback(teacher=teacher_id).pack()

        text = f"{last_name} {first_name} {middle_name}"
        if len(text) > 50:
            text = text[:50] + "..."
        builder.button(text=text, callback_data=callback)

    builder.adjust(1)

    builder.row(InlineKeyboardButton(text="<< Назад", callback_data=TeacherTextCallback(teacher="Назад").pack()))

    return builder.as_markup()
