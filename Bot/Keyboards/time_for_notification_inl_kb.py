from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NotificationTimeCallback(CallbackData, prefix="notification_apply"):
    notification_time: str


def notification_time_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="00:00", callback_data=NotificationTimeCallback(notification_time="00").pack())
    builder.button(text="01:00", callback_data=NotificationTimeCallback(notification_time="01").pack())
    builder.button(text="02:00", callback_data=NotificationTimeCallback(notification_time="02").pack())
    builder.button(text="03:00", callback_data=NotificationTimeCallback(notification_time="03").pack())
    builder.button(text="04:00", callback_data=NotificationTimeCallback(notification_time="04").pack())
    builder.button(text="05:00", callback_data=NotificationTimeCallback(notification_time="05").pack())
    builder.button(text="06:00", callback_data=NotificationTimeCallback(notification_time="06").pack())
    builder.button(text="07:00", callback_data=NotificationTimeCallback(notification_time="07").pack())
    builder.button(text="08:00", callback_data=NotificationTimeCallback(notification_time="08").pack())
    builder.button(text="09:00", callback_data=NotificationTimeCallback(notification_time="09").pack())

    builder.adjust(2)

    return builder.as_markup()