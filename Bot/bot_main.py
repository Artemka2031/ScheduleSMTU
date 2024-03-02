import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.Routers.MailingRouter.mail_router import MailRouter
from Bot.Routers.RoleRouter.role_router import RoleRouter
from Bot.Routers.SettingsRouter.change_group_suggestions_router import SettingsRouter
from Routers.StartRouter import StartRouter, RegistrationRouter
from Bot.Routers.ScheduleRouter.temp_week_schedule_router import ScheduleRouter
from bot_initialization import bot, default_commands



async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    await default_commands()

    dp.include_router(RoleRouter)

    dp.include_router(StartRouter)

    dp.include_router(ScheduleRouter)

    dp.include_router(MailRouter)

    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
