from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin_bot.RabbitMQProducer.producer_api import send_request_mq

class ClassTimeCallback(CallbackData, prefix="classtime"):
    classtime_id: int | str

async def classtime_kb():
    builder = InlineKeyboardBuilder()

    all_pare_start = await send_request_mq('bot.tasks.get_all_pare_start_time', [])

    if not isinstance(all_pare_start, dict):
        print("Ошибка: неверный формат ответа от брокера сообщений")
        return builder.as_markup()

    for pare_time, pare_id in all_pare_start.items():
        builder.button(text=str(pare_time), callback_data=ClassTimeCallback(classtime_id=pare_id).pack())

    # Добавляем кнопку "Весь день"
    builder.button(text="Весь день", callback_data=ClassTimeCallback(classtime_id=9).pack())

    builder.adjust(2)

    back_button = InlineKeyboardButton(
        text='<< Назад',
        callback_data=ClassTimeCallback(classtime_id='cancel').pack()
    )

    # Добавляем кнопку "Назад" на отдельную строку
    builder.row(back_button)

    return builder.as_markup()