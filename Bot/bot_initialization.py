from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from ORM.Tables.UserTables.user_table import User
from config import token

bot = Bot(token=str(token.get("token")), parse_mode=ParseMode.HTML)


async def setup_bot_commands(status: str, user_id: int | str):
    await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))
    if status == "user":

        user_commands = [
            BotCommand(command="change_group", description="Поменять номер группы"),
            BotCommand(command="suggestion", description="Оставить пожелание (максимум - 4 в день)"),
            BotCommand(command="notification", description="Отправлять расписание на день в заданное время")
        ]
        await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=user_id))

    elif status == "admin":
        admin_commands = [
            BotCommand(command="mailing", description="Отправить рассылку"),
            BotCommand(command="suggestion_reply", description="Ответить на предложение"),
            BotCommand(command="vuc", description="Добавить расписание на военную кафедру")
        ]
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user_id))

    else:
        print("Неверный статус пользователя")
        return


# Без этой функции админам исходно выдается админ-панель
async def default_commands():
    for user_id in User.get_all_users_ids():
        await setup_bot_commands("user", user_id)
