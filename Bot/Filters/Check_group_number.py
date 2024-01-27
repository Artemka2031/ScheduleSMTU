from aiogram.filters import Filter
from aiogram.types import Message

from ORM.Schedule_information import Group


class CheckGroupFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        try:
            group_number = int(message.text)
        except ValueError:
            return False

        try:
            Group.get_group_id(group_number)
        except ValueError:
            return False

        return True
