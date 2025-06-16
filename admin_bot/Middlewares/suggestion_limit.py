from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message

from admin_bot.RabbitMQProducer.producer_api import send_request_mq
from admin_bot.bot_initialization import bot
# from djcore.apps.database.utils.UserTables.suggestion_table import BaseSuggestion


class SuggestionLimitMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        user_suggestion_count = await send_request_mq('bot.tasks.get_user_suggestions_count', [event.from_user.id])

        if user_suggestion_count >= 4:
            await bot(
                SendMessage(
                    chat_id=event.from_user.id,
                    text='Вы использовали максимальное количество пожеланий. Пожалуйста, попробуйте завтра.'
                )
            )

            return None

        return await handler(event, data)
