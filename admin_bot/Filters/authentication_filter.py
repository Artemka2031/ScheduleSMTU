import logging

from aiogram.filters import Filter
from aiogram.types import Message
from admin_bot.RabbitMQProducer.producer_api import send_request_mq


class isRegFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        try:
        # Отправляем запрос и ожидаем ответа
            user_data = await send_request_mq('admin_bot.tasks.get_user', [message.from_user.id])
        except Exception as e:
            print(f"Возникла ошибка при связи с брокером сообщений: {e}")
            return False
        # Обрабатываем результат
        if user_data is None:
            # Если None, значит пользователь не найден
            return False
        else:
            print(f"Пользователь найден: {user_data}")
            return True
