from aiogram.filters import Filter
from aiogram.types import Message

from ORM.Tables.UserTables.user_table import User


class isRegFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        if User.get_user(message.from_user.id) is None:
            return False

        return True
