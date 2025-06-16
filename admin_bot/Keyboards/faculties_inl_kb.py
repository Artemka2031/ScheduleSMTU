from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin_bot.RabbitMQProducer.producer_api import send_request_mq

class FacultyCallback(CallbackData, prefix="faculty"):
    faculty_id: int


async def add_faculty_kb():
    builder = InlineKeyboardBuilder()

    all_faculties = await send_request_mq('bot.tasks.get_all_faculties', [])

    if not isinstance(all_faculties, dict):
        print("Ошибка: некорректный формат ответа от брокера сообщений")
        return builder.as_markup()

    for faculty_name, faculty_id in all_faculties.items():
        builder.button(text=str(faculty_name), callback_data=FacultyCallback(faculty_id=faculty_id).pack())

    builder.adjust(1)

    return builder.as_markup()