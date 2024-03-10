from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.Routers.MenuRouter import MenuRouter
from Bot.Routers.MailingRouter.mail_router import MailRouter
from Bot.Routers.RoleRouter.role_router import RoleRouter
from Bot.Routers.ScheduleRouter import ScheduleRouter
from Bot.Routers.SettingsRouter import SettingsRouter
from Bot.Routers.StartRouter import StartRouter, RegistrationRouter
from Bot.bot_initialization import bot, default_commands


async def start_bot():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    await default_commands()

    dp.include_router(RoleRouter)

    dp.include_router(StartRouter)

    dp.include_router(ScheduleRouter)

    dp.include_router(MenuRouter)

    dp.include_router(MailRouter)

    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    await dp.start_polling(bot)

# if __name__ == '__main__':
#
#     asyncio.run(start_bot())
#     try:
#         print("Бот запущен")
#     except Exception as e:
#         print('Закрываю бота')
