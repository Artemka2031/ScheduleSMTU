from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def today_tomorrow_rep_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="Сегодня"),
        KeyboardButton(text="Завтра")
    )

    builder.row(
        KeyboardButton(text="Расписание")
    )

    return builder.as_markup(resize_keyboard=True)
