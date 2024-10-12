import os
import sys
import aio_pika
import json
import logging

# Добавляем путь к корневой директории вашего проекта в sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcore.settings')

# Инициализация Django (если нужно)
from djcore.settings import RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_HOST, RABBITMQ_PORT
from djcore.celery_app import app

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USER,
            password=RABBITMQ_PASSWORD
        )
        self.channel = await self.connection.channel()

        # Объявляем exchange
        self.exchange = await self.channel.declare_exchange('direct_exchange', aio_pika.ExchangeType.DIRECT, durable=True)
        # Объявляем очередь
        self.queue = await self.channel.declare_queue('bot_queue', durable=True)
        # Связываем очередь с exchange и routing_key
        await self.queue.bind(self.exchange, routing_key='bot.tasks.*')

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                data = json.loads(body)
                if isinstance(data, dict) and 'task' in data and 'data' in data:
                    task_name = data['task']
                    task_data = data['data']
                    reply_to = message.reply_to
                    correlation_id = message.correlation_id
                    logger.exception(f"Получена задача: {task_name} с данными: {reply_to, correlation_id}")
                    if task_name not in app.tasks.keys():
                        logger.error(f"Задача {task_name} не найдена в Celery.")
                        raise ValueError("Задача не найдена в Celery")

                    # Отправляем задачу в Celery с аргументами reply_to и correlation_id
                    task = app.tasks[task_name]
                    logger.exception(task_data)
                    task.apply_async(args=task_data, kwargs={'reply_to': reply_to, 'correlation_id': correlation_id})
            except Exception as e:
                logger.exception("Ошибка при обработке сообщения")

    async def start_consuming(self):
        await self.connect()
        await self.queue.consume(self.process_message)
        logger.info("Запуск асинхронного RabbitMQ Consumer для очереди bot_queue")

# def start_consumer():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     consumer = RabbitMQConsumer()
#
#     # Создаем задачу для старта consumer
#     loop.create_task(consumer.start_consuming())
#
#     # Бесконечно запускаем цикл событий
#     try:
#         loop.run_forever()
#     except (KeyboardInterrupt, SystemExit):
#         pass
#     finally:
#         pending = asyncio.all_tasks(loop)
#         for task in pending:
#             task.cancel()
#         loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))  # Ожидаем завершения всех задач
#         loop.run_until_complete(loop.shutdown_asyncgens())  # Очищаем асинхронные генераторы
#         loop.close()

# if __name__ == '__main__':
#     start_consumer()
