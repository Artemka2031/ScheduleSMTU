from aiogram.filters import Filter
from aiogram.types import Message

#from djcore.apps.database.utils.SceduleTables import Group
#from djcore.apps.database.utils.UserTables.user_table import BaseUser
from Bot.RabbitMQProducer.producer_api import send_request_mq

class CheckGroupFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        try:
            group_number = int(message.text)
        except ValueError:
            return False

        try:
            group_exists = await send_request_mq('bot.tasks.get_group_id', [group_number])
        except Exception as e:
            print(f"Возникла ошибка при связи с брокером сообщений: {e}")
            return False

        if group_exists:
            return True
        else:
            return False


class CheckCurrentGroupFilter(Filter):

    async def __call__(self, message: Message) -> bool:

        current_group = await send_request_mq('bot.tasks.get_group_number', [message.from_user.id])

        if current_group == int(message.text):
            return False

        return True
