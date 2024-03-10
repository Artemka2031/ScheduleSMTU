from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class WeekTypeCallback(CallbackData, prefix="week_type"):
    week_type: str


def week_type_kb(back_to_menu: bool = False):
    builder = InlineKeyboardBuilder()

    builder.button(text="Верхняя неделя", callback_data=WeekTypeCallback(week_type="Верхняя неделя").pack())
    builder.button(text="Обе недели", callback_data=WeekTypeCallback(week_type="Обе недели").pack())
    builder.button(text="Нижняя неделя", callback_data=WeekTypeCallback(week_type="Нижняя неделя").pack())

    if back_to_menu:
        builder.button(text="<< Назад", callback_data=WeekTypeCallback(week_type="Назад").pack())

    builder.adjust(1)

    return builder.as_markup()


class WeekDayCallback(CallbackData, prefix="week_day"):
    week_day: str


def week_day_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Понедельник", callback_data=WeekDayCallback(week_day="Понедельник").pack())
    builder.button(text="Вторник", callback_data=WeekDayCallback(week_day="Вторник").pack())
    builder.button(text="Среда", callback_data=WeekDayCallback(week_day="Среда").pack())
    builder.button(text="Четверг", callback_data=WeekDayCallback(week_day="Четверг").pack())
    builder.button(text="Пятница", callback_data=WeekDayCallback(week_day="Пятница").pack())
    builder.button(text="Суббота", callback_data=WeekDayCallback(week_day="Суббота").pack())

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="<< Назад", callback_data=WeekDayCallback(week_day="Назад").pack()))

    return builder.as_markup()
