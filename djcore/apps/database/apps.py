import asyncio
import threading

from django.apps import AppConfig

from djcore.apps.database.rabbitmq_consumer import RabbitMQConsumer
from djcore.celery_app import app


def start_consumer():
    app.autodiscover_tasks()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    consumer = RabbitMQConsumer()

    # Создаем задачу для старта consumer
    loop.create_task(consumer.start_consuming())

    # Бесконечно запускаем цикл событий
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))  # Ожидаем завершения всех задач
        loop.run_until_complete(loop.shutdown_asyncgens())  # Очищаем асинхронные генераторы
        loop.close()

class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djcore.apps.database'

    def ready(self):
        # Задержка перед запуском RabbitMQConsumer, чтобы Django успел корректно запуститься
        def delayed_start():
            import time
            time.sleep(7)  # Ожидаем 5 секунд перед стартом Consumer
            start_consumer()

        # Запускаем consumer в отдельном потоке
        thread = threading.Thread(target=delayed_start, daemon=True)
        thread.start()