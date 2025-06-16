from aiogram import Router

from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.by_time import ScheduleByTimeRouter
from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.teachers_text_router import TeacherRouter
from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.free_audience import AudienceRouter
from admin_bot.Middlewares import IsRegMiddleware

ScheduleRouter = Router()

ScheduleRouter.message.middleware(IsRegMiddleware())


ScheduleRouter.include_router(ScheduleByTimeRouter)
ScheduleRouter.include_router(TeacherRouter)
ScheduleRouter.include_router(AudienceRouter)

