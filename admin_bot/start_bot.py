import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from admin_bot.Routers import MailRouter, RepSuggestionRouter, RoleRouter, ScheduleRouter, SettingsRouter, \
    StartRouter, RegistrationRouter

from admin_bot.bot_initialization import bot, default_commands


async def start_bot():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    await default_commands()

    dp.include_router(RoleRouter)

    dp.include_router(StartRouter)

    dp.include_router(ScheduleRouter)

    dp.include_router(MailRouter)

    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    dp.include_router(RepSuggestionRouter)

    await dp.start_polling(bot)

if __name__ == '__main__':

    asyncio.run(start_bot())
    try:
        print("Бот запущен")
    except Exception as e:
        print('Закрываю бота')
