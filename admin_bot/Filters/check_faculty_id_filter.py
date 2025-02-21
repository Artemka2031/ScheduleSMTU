from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from admin_bot.Keyboards.faculties_inl_kb import FacultyCallback
from admin_bot.RabbitMQProducer.producer_api import send_request_mq

class CheckCurrentFacultyFilter(BaseFilter):

    async def __call__(self, call: CallbackQuery, callback_data: FacultyCallback) -> bool:
        try:
        # Отправляем запрос и ожидаем ответа
            current_faculty_id = await send_request_mq('admin_bot.tasks.get_faculty_id', [call.from_user.id])
        except Exception as e:
            print(f"Возникла ошибка при связи с брокером сообщений: {e}")
            return False

        if current_faculty_id == callback_data.faculty_id:
            return False

        return True
