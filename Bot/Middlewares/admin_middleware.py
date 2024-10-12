from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message
from Bot.RabbitMQProducer.producer_api import send_request_mq
from Bot.bot_initialization import bot


# admins = [964593325, 410191942]

class IsAdmMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        admins_list = await send_request_mq("bot.tasks.get_all_admins", [])


        if event.from_user.id not in admins_list:
            await bot(
                SendMessage(chat_id=event.from_user.id,
                            text="У вас недостаточно прав для выполнения этой команды"))
            return None

        return await handler(event, data)
