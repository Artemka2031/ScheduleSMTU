import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.backoff import BackoffConfig

from admin_bot.Routers import MailRouter, RepSuggestionRouter, RoleRouter, ScheduleRouter, SettingsRouter, \
    StartRouter, RegistrationRouter

from admin_bot.bot_initialization import bot, default_commands


async def start_bot():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    backoff_config = BackoffConfig(
        min_delay=1.0,  # Минимальная задержка (секунды)
        max_delay=60.0,  # Максимальная задержка
        factor=2.0,  # Множитель задержки
        jitter=0.1  # Случайное отклонение
    )
    await default_commands()

    dp.include_router(RoleRouter)

    dp.include_router(StartRouter)

    dp.include_router(ScheduleRouter)

    dp.include_router(MailRouter)

    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    dp.include_router(RepSuggestionRouter)

    await dp.start_polling(bot, backoff_config=backoff_config)

if __name__ == '__main__':

    asyncio.run(start_bot())
    try:
        print("Бот запущен")
    except Exception as e:
        print('Закрываю бота')
