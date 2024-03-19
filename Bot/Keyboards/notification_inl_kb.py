from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NotificationCallback(CallbackData, prefix="notification_apply"):
    notification_apply: str


def notification_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Да", callback_data=NotificationCallback(notification_apply="Да").pack())
    builder.button(text="Нет", callback_data=NotificationCallback(notification_apply="Нет").pack())
    builder.button(text="Отписаться", callback_data=NotificationCallback(notification_apply="Отписаться").pack())

    builder.adjust(2)

    return builder.as_markup()