import functools

import aio_pika
import json
import uuid
import asyncio
import logging
from admin_bot.RabbitMQProducer.mq_config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_PORT

class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.response_queue_obj = None
        self.response_queue = 'django_response_admin_queue'
        self.routing_key = 'admin_bot_queue'
        self.pending_responses = {}
        self.listener_ready = asyncio.Event()
        self.consumer_tag = None  # Добавляем событие для синхронизации
        self.response_queues = {}  # Словарь очередей ответов по correlation_id
        self.exchange = None

    async def connect(self):
        RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'
        try:
            logging.info(f"Подключаюсь к RabbitMQ по адресу {RABBITMQ_URL}")
            self.connection = await aio_pika.connect_robust(
                RABBITMQ_URL
            )
            self.channel = await self.connection.channel()

            # Объявляем exchange
            self.exchange = await self.channel.declare_exchange('direct_exchange', aio_pika.ExchangeType.DIRECT, durable=True)
            logging.info("Обменник 'direct_exchange' объявлен успешно.")

            # Объявляем очередь для ответов
            self.response_queue_obj = await self.channel.declare_queue(self.response_queue, durable=True)
            await self.response_queue_obj.bind(self.exchange, routing_key=self.response_queue)
            logging.info(f"Очередь ответов '{self.response_queue}' объявлена успешно.")

            # Начинаем слушать очередь ответов и сохраняем ссылку на задачу
            self.consumer_tag = await self.response_queue_obj.consume(functools.partial(self.on_message))

            # Сигнализируем, что слушатель запущен
            self.listener_ready.set()

            # Ждём, пока слушатель не будет готов
            await self.listener_ready.wait()
        except Exception as e:
            logging.error(f"Ошибка при подключении к RabbitMQ: {e}")

    async def send_message(self, message):
        try:
            correlation_id = str(uuid.uuid4())
            response_queue = asyncio.Queue()
            self.response_queues[correlation_id] = response_queue

            logging.info(f"Отправка сообщения в RabbitMQ с correlation_id {correlation_id}")

            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    correlation_id=correlation_id,
                    reply_to=self.response_queue
                ),
                routing_key=self.routing_key
            )

            # Ожидаем ответа из очереди
            logging.info(f"Ожидание ответа для correlation_id {correlation_id}")
            #logging.info(self.response_queues)
            result = await response_queue.get()

            logging.info(f"Получен ответ для correlation_id {correlation_id}: {result}")
            return result['result']
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения или получении ответа: {e}")
        finally:
            self.response_queues.pop(correlation_id, None)
            # Удаляем очередь ответа


    async def on_message_async(self, message: aio_pika.IncomingMessage):
        #logging.info("on_message_async callback вызван")
        async with message.process():
            correlation_id = message.correlation_id
            logging.info(f"Получено сообщение с correlation_id: {correlation_id}")
            if correlation_id and correlation_id in self.response_queues:
                logging.info(f"Получен ожидаемый ответ с correlation_id {correlation_id}")
                response = json.loads(message.body.decode())
                response_queue = self.response_queues.get(correlation_id)
                if response_queue:
                    await response_queue.put(response)
                else:
                    logging.warning(f"Очередь ответа не найдена для correlation_id: {correlation_id}")
            else:
                logging.warning(f"Получен неизвестный ответ с correlation_id: {correlation_id}")

    def on_message(self, message: aio_pika.IncomingMessage):
        # Оборачиваем вызов асинхронной функции через asyncio
        asyncio.create_task(self.on_message_async(message))


    async def close(self):
        if self.connection:
            logging.info("Закрытие подключения к RabbitMQ.")

            # Отменяем потребление сообщений
            if self.consumer_tag:
                await self.response_queue_obj.cancel(self.consumer_tag)
                logging.info("Слушатель очереди ответов был отменен.")

            await self.connection.close()
