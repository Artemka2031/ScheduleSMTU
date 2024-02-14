import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Bot.Routers.SettingsRouter.change_group_suggestions_router import SettingsRouter
from Routers.StartRouter import StartRouter, RegistrationRouter
from Bot.Routers.ScheduleRouter.temp_week_schedule_router import ScheduleRouter
from bot_initialization import bot
from Mailing.mailing_function import MailRouter

async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(StartRouter)

    # dp.include_router(tempRouter)
    # dp.include_router(WeekScheduleRouter)
    dp.include_router(ScheduleRouter)

    dp.include_router(MailRouter)

    # dp.include_router(SuggestionRouter)
    # dp.include_router(ChangeGroupRouter)
    dp.include_router(SettingsRouter)

    dp.include_router(RegistrationRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
