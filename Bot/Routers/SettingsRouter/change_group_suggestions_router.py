from aiogram import Router

from Bot.Routers.SettingsRouter.SettingsRouters import ChangeGroupRouter, SuggestionRouter

from Bot.Middlewares import IsRegMiddleware

SettingsRouter = Router()

SettingsRouter.message.middleware(IsRegMiddleware())


SettingsRouter.include_router(ChangeGroupRouter)
SettingsRouter.include_router(SuggestionRouter)


