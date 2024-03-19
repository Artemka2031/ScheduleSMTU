from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TypeWeekVucCallback(CallbackData, prefix="this_next_week"):
    week_type: str


def add_schedule_vuc_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Эта неделя", callback_data=TypeWeekVucCallback(week_type="Эта неделя").pack())
    builder.button(text="Следующая неделя", callback_data=TypeWeekVucCallback(week_type="Следующая неделя").pack())

    builder.adjust(2)

    return builder.as_markup()