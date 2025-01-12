from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djcore.apps.database'

    def ready(self):
        # Здесь больше не запускаем RabbitMQConsumer
        print("Приложение DatabaseConfig готово к работе.")