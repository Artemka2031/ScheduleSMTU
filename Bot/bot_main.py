import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Routers.StartRouter import StartRouter, RegistrationRouter
from Routers.ScheduleRouters import tempRouter, WeekScheduleRouter
from Routers.SettingsRouter import SuggestionRouter, ChangeGroupRouter
from bot_initialization import bot


async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(StartRouter)

    dp.include_router(tempRouter)
    dp.include_router(WeekScheduleRouter)

    dp.include_router(SuggestionRouter)
    dp.include_router(ChangeGroupRouter)

    dp.include_router(RegistrationRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
