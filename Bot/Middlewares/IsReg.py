from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message

from Bot.create_bot import bot
from ORM.Users_info import User


class IsRegMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not User.get_user(event.from_user.id):
            await bot(
                SendMessage(chat_id=event.from_user.id,
                            text='Чтобы использовать бота нужно зарегистрироваться. \nНапишите /registration.'))
            return None

        return await handler(event, data)
