from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.methods import SendMessage
from aiogram.types import Message

from Bot.bot_initialization import bot
from ORM.Tables.UserTables.suggestion_table import Suggestion


class SuggestionLimitMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if Suggestion.get_user_suggestions_count(event.from_user.id) >= 4:
            await bot(
                SendMessage(
                    chat_id=event.from_user.id,
                    text='Вы использовали максимальное количество пожеланий. Пожалуйста, попробуйте завтра.'
                )
            )

            return None

        return await handler(event, data)
