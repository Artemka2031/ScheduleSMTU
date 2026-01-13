import os
import asyncio
import sys
import signal
import time
import django
import threading

# Инициализация Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcore.settings')
django.setup()

from djcore.apps.database.rabbitmq_consumer import RabbitMQConsumer
from djcore.celery_app import app


class RabbitMQConsumerRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.consumer = RabbitMQConsumer()
        self.shutdown_event = asyncio.Event()

    async def start(self):
        print("Запуск RabbitMQ Consumer...")
        app.autodiscover_tasks()

        consumer_task = asyncio.create_task(self.consumer.start_consuming())

        await self.shutdown_event.wait()

        print("Остановка RabbitMQ Consumer...")
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass

    def stop(self):
        self.shutdown_event.set()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())


async def main():
    consumer_runner = RabbitMQConsumerRunner()

    consumer_thread = threading.Thread(target=consumer_runner.run, daemon=True)
    consumer_thread.start()

    # Windows-совместимый обработчик сигналов
    def handle_signal(signum, frame):
        print(f"Получен сигнал {signum}, останавливаем consumer...")
        consumer_runner.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while consumer_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Прерывание пользователем. Завершаем...")
        consumer_runner.stop()
        consumer_thread.join()


if __name__ == "__main__":
    # Даем Django время запуститься
    time.sleep(1)

    # Запуск основного цикла
    asyncio.run(main())
