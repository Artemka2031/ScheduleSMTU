from aiogram import Router

from Bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters import TodayTomorrowRouter, WeekScheduleRouter

from Bot.Middlewares import IsRegMiddleware

ScheduleRouter = Router()

ScheduleRouter.message.middleware(IsRegMiddleware())


ScheduleRouter.include_router(TodayTomorrowRouter)
ScheduleRouter.include_router(WeekScheduleRouter)


