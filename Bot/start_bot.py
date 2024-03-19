from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.Routers import MailRouter, RepSuggestionRouter, RoleRouter, MenuRouter, ScheduleRouter, SettingsRouter, \
    StartRouter, RegistrationRouter, NotificationRouter, AddScheduleVucRouter, VucRouter
from Bot.Routers.AdminRouters.AddScheduleVucRouter.vuc_scheduler import vuc_scheduler
from Bot.Routers.UserRouters.NotificationRouter.notification_scheduler import notification_scheduler
from Bot.bot_initialization import bot, default_commands


async def start_bot():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    await default_commands()

    dp.include_router(RoleRouter)

    dp.include_router(StartRouter)

    dp.include_router(NotificationRouter)

    dp.include_router(ScheduleRouter)

    dp.include_router(MenuRouter)

    dp.include_router(VucRouter)

    dp.include_router(MailRouter)

    dp.include_router(AddScheduleVucRouter)

    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    dp.include_router(RepSuggestionRouter)

    await notification_scheduler()

    await vuc_scheduler()

    await dp.start_polling(bot)

# if __name__ == '__main__':
#
#     asyncio.run(start_bot())
#     try:
#         print("Бот запущен")
#     except Exception as e:
#         print('Закрываю бота')
