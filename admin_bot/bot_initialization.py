import pytz
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from admin_bot.RabbitMQProducer.producer_api import send_request_mq

bot = Bot(token="7959076358:AAHqkpQJPdMcP6YaKhJMxgEVRGGnb4sLgJU")
moscow_tz = pytz.timezone('Europe/Moscow')

async def setup_bot_commands(status: str, user_id: int | str):
    await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))
    if status == "user":

        user_commands = [
            BotCommand(command="change_faculty", description="Поменять факультет"),
            BotCommand(command="suggestion", description="Оставить пожелание (максимум - 4 в день)")
        ]
        await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=user_id))

    elif status == "admin":
        admin_commands = [
            BotCommand(command="mailing", description="Отправить рассылку"),
            BotCommand(command="suggestion_reply", description="Ответить на предложение")
        ]
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user_id))

    else:
        print("Неверный статус пользователя")
        return


# Без этой функции админам исходно выдается админ-панель
async def default_commands():
    all_users_ids = await send_request_mq('admin_bot.tasks.get_all_users_ids', [])

    if all_users_ids:
        for user_id in all_users_ids:
            await setup_bot_commands("user", user_id)

