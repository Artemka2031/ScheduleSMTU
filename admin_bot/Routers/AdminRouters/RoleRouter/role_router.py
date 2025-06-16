from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from admin_bot.Middlewares.admin_middleware import IsAdmMiddleware

from admin_bot.bot_initialization import setup_bot_commands

RoleRouter = Router()
RoleRouter.message.middleware(IsAdmMiddleware())


@RoleRouter.message(Command("user"))
async def send_role(message: Message):
    status = "user"
    await message.answer(text="Вы - пользователь")
    await setup_bot_commands(status, message.from_user.id)


@RoleRouter.message(Command("admin"))
async def send_role(message: Message):
    status = "admin"
    await message.answer(text="Вы - админ")
    await setup_bot_commands(status, message.from_user.id)
