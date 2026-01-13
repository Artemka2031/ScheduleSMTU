from typing import List, Dict

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CanselMenuCallback(CallbackData, prefix="CMC"):
    cansel: bool


class MenuCallback(CallbackData, prefix="MNC"):
    operation: str


def create_menu_kb(cansel: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Твоя группа", callback_data=MenuCallback(operation="schedule").pack())
    builder.button(text="Твои преподаватели", callback_data=MenuCallback(operation="teachers").pack())

    builder.adjust(2)

    if cansel:
        builder.row(InlineKeyboardButton(text="Отмена", callback_data=CanselMenuCallback(cansel=True).pack()))

    return builder.as_markup()


class TeacherCallback(CallbackData, prefix="TC"):
    teacher: int | str


def create_teachers_kb(teachers: List[Dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for teacher in teachers:
        last_name = teacher["last_name"]
        first_name = teacher["first_name"]
        middle_name = teacher["middle_name"]
        teacher_id = teacher["id"]

        if last_name == "":
            continue

        callback = TeacherCallback(teacher=teacher_id).pack()

        builder.button(text=f"{last_name} {first_name[0]}. {middle_name[0]}.", callback_data=callback)

    builder.adjust(2)

    builder.row(InlineKeyboardButton(text="<< Назад", callback_data=TeacherCallback(teacher="Назад").pack()))

    return builder.as_markup()


