from aiogram import Bot
from aiogram.enums import ParseMode
from ORM.Tables.UserTables.user_table import User
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from config import token

bot = Bot(token=str(token.get("token")), parse_mode=ParseMode.HTML)


async def setup_bot_commands(status: str, user_id: int | str):
    if status == "user":
        await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))

        user_commands = [
            BotCommand(command="change_group", description="Поменять номер группы"),
            BotCommand(command="week_schedule", description="Посмотреть расписание на конкретный день"),
            BotCommand(command="suggestion", description="Оставить пожелание (максимум - 4 в день)")
        ]
        await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    elif status == "admin":
        await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=user_id))
        admin_commands = [
            BotCommand(command="mailing", description="Отправить рассылку"),
            BotCommand(command="suggestion_reply", description="Ответить на предложение")
        ]
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user_id))

    else:
        print("Неверный статус пользователя")
        return

#Без этой функции админам исходно выдается админ-панель
async def default_commands():
    for user_id in User.get_all_users_ids():
        await setup_bot_commands("user", user_id)
