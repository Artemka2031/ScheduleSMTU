from aiogram import Router

from Bot.Routers.ScheduleRouter.ScheduleRouters import tempRouter, WeekScheduleRouter

from Bot.Middlewares import IsRegMiddleware

ScheduleRouter = Router()

ScheduleRouter.message.middleware(IsRegMiddleware())


ScheduleRouter.include_router(tempRouter)
ScheduleRouter.include_router(WeekScheduleRouter)


