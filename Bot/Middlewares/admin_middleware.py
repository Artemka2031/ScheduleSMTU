from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message

from Bot.bot_initialization import bot
from ORM.Tables.UserTables.user_table import User

admins = [964593325, 410191942]

class IsAdmMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if User.user_id not in admins:
            await bot(
                SendMessage(chat_id=event.from_user.id,
                            text="У вас недостаточно прав для выполнения этой команды"))
            return None

        return await handler(event, data)
