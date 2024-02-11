from aiogram.utils.keyboard import ReplyKeyboardBuilder


def today_tomorrow_rep_keyboard():
    today_tomorrow_rep_kb = ReplyKeyboardBuilder()

    today_tomorrow_rep_kb.button(text="Сегодня")
    today_tomorrow_rep_kb.button(text="Завтра")

    today_tomorrow_rep_kb.adjust(2)

    return today_tomorrow_rep_kb.as_markup(resize_keyboard=True)
