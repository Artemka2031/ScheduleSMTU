from aiogram.filters import Filter
from aiogram.types import Message


class isNotComandFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        if message.text[0] == '/':
            return False

        return True
