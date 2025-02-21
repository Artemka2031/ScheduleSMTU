from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="По времени"),
        KeyboardButton(text="По преподавателю")
    )

    builder.row(
        KeyboardButton(text="Фонд аудиторий")
    )

    return builder.as_markup(resize_keyboard=True)
