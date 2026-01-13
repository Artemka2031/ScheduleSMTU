from aiogram import Router

from admin_bot.Routers.UserRouters.SettingsRouter.SettingsRouters import SuggestionRouter
from admin_bot.Routers.UserRouters.SettingsRouter.SettingsRouters.change_faculty import ChangeFacultyRouter

from admin_bot.Middlewares import IsRegMiddleware

SettingsRouter = Router()

SettingsRouter.message.middleware(IsRegMiddleware())


SettingsRouter.include_router(ChangeFacultyRouter)
SettingsRouter.include_router(SuggestionRouter)


