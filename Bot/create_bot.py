from aiogram import Bot
from aiogram.enums import ParseMode

from config import token

bot = Bot(token=str(token.get("token")), parse_mode=ParseMode.HTML)
