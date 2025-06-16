from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message

from Bot.RabbitMQProducer.producer_api import send_request_mq
from Bot.bot_initialization import bot
# from djcore.apps.database.utils.UserTables.user_table import BaseUser


class IsRegMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        user_is_registered = await send_request_mq('bot.tasks.get_user', [event.from_user.id])


        if not user_is_registered:
            await bot(
                SendMessage(chat_id=event.from_user.id,
                            text='Чтобы использовать бота нужно зарегистрироваться. \nНапишите /registration.'))
            return None

        return await handler(event, data)