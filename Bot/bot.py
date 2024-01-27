import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Routers.ScheduleRouters import tempRouter
from Routers.SettingsRouter import InitializationRouter, ChangeGroupRouter
from create_bot import bot


async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(InitializationRouter)
    dp.include_router(tempRouter)
    dp.include_router(ChangeGroupRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
