import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ORM.create_database import Group
from Routers.StartRouter import startRouter
from Routers.ScheduleRouters import tempRouter
from create_bot import bot


async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(startRouter)
    dp.include_router(tempRouter)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
