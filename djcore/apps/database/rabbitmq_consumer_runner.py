import asyncio
import threading
import time
import signal

# Инициализация Django (чтобы получить доступ к settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcore.settings')
django.setup()

from djcore.apps.database.rabbitmq_consumer import RabbitMQConsumer
from djcore.celery_app import app


class RabbitMQConsumerRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.consumer = RabbitMQConsumer()
        self.thread = None

    def start(self):
        print("Запуск RabbitMQ Consumer...")
        app.autodiscover_tasks()

        def run():
            try:
                # Создаем задачу для запуска потребителя
                self.loop.create_task(self.consumer.start_consuming())
                # Бесконечно запускаем цикл событий
                self.loop.run_forever()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                print("Завершение работы RabbitMQ Consumer...")
                self._stop_loop()

        # Запускаем поток
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        print("Остановка RabbitMQ Consumer...")
        self._stop_loop()
        if self.thread:
            self.thread.join()

    def _stop_loop(self):
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.stop()
        self.loop.close()


def signal_handler(consumer_runner, *args):
    consumer_runner.stop()
    print("Приложение остановлено.")
    exit(0)


if __name__ == "__main__":
    consumer_runner = RabbitMQConsumerRunner()

    # Обрабатываем сигналы для корректного завершения
    signal.signal(signal.SIGINT, lambda *args: signal_handler(consumer_runner, *args))
    signal.signal(signal.SIGTERM, lambda *args: signal_handler(consumer_runner, *args))

    # Задержка перед запуском, чтобы все службы Django успели стартовать
    time.sleep(3.5)

    # Запускаем consumer
    consumer_runner.start()

    # Блокируем выполнение, чтобы основной поток не завершался
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        consumer_runner.stop()
        print("RabbitMQ Consumer остановлен.")