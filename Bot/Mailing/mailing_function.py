from aiogram.methods import SendMessage

from Bot.bot_initialization import bot
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command

from ORM.Tables.UserTables.user_table import User

MailRouter = Router()


@MailRouter.message(Command("mailing"))
async def send_mailing(message: Message):
    user_ids = User.get_all_users()
    for id in user_ids:
        await bot(SendMessage(chat_id=id, text=f"Письмо отправлено пользователю {id}"))
