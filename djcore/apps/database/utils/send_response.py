import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcore.settings')

# Инициализация Django (если нужно)
from djcore.settings import RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_HOST, RABBITMQ_PORT

import json
import logging
import aio_pika
import asyncio

async def send_response(result, reply_to, correlation_id):

    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )

    async with connection:
        channel = await connection.channel()


        # Объявляем очередь для reply_to
        queue = await channel.declare_queue(reply_to, durable=True)
        exchange = await channel.declare_exchange('direct_exchange', aio_pika.ExchangeType.DIRECT, durable=True)
        await queue.bind(exchange, routing_key=reply_to)

        # Формируем и отправляем сообщение с результатом
        message = aio_pika.Message(
            body=json.dumps(result).encode(),
            correlation_id=correlation_id
        )
        logging.info(f'Очередь ответов {reply_to}\nСам ответ - {result}')
        # Публикуем сообщение с использованием reply_to в качестве routing_key
        await exchange.publish(
            message,
            routing_key=reply_to
        )
