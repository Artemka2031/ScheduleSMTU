from aiogram import Router

from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters import TodayTomorrowRouter

from admin_bot.Middlewares import IsRegMiddleware

ScheduleRouter = Router()

ScheduleRouter.message.middleware(IsRegMiddleware())


ScheduleRouter.include_router(TodayTomorrowRouter)


