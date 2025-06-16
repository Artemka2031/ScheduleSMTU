import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.backoff import BackoffConfig

from Bot.RabbitMQProducer.rabbitmq_producer import RabbitMQProducer
from Bot.Routers import MailRouter, RepSuggestionRouter, RoleRouter, MenuRouter, ScheduleRouter, SettingsRouter, \
    StartRouter, RegistrationRouter, NotificationRouter

from Bot.Routers.UserRouters.NotificationRouter.notification_scheduler import notification_scheduler
from Bot.bot_initialization import bot, default_commands

# Добавляем логирование для отладки
logging.basicConfig(level=logging.INFO)

async def start_bot():
    try:
        logging.info("Инициализация хранилища и диспетчера...")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        backoff_config = BackoffConfig(
            min_delay=1.0,  # Минимальная задержка (секунды)
            max_delay=60.0,  # Максимальная задержка
            factor=2.0,  # Множитель задержки
            jitter=0.1  # Случайное отклонение
        )

        logging.info("Установка команд бота...")
        await default_commands()

        logging.info("Подключение роутеров...")
        dp.include_router(RoleRouter)
        dp.include_router(StartRouter)
        dp.include_router(NotificationRouter)
        dp.include_router(ScheduleRouter)
        dp.include_router(MenuRouter)
        dp.include_router(MailRouter)
        dp.include_router(SettingsRouter)
        dp.include_router(RegistrationRouter)
        dp.include_router(RepSuggestionRouter)

        logging.info("Запуск планировщика уведомлений...")
        await notification_scheduler()

        logging.info("Запуск лонг-поллинга...")

        await dp.start_polling(bot, backoff_config=backoff_config)

    except Exception as e:
        logging.error(f"Произошла ошибка при запуске бота: {e}")
        raise


if __name__ == '__main__':
    try:
        logging.info("Запуск бота...")
        asyncio.run(start_bot())
    except Exception as e:
        logging.error(f"Бот завершил работу с ошибкой: {e}")
