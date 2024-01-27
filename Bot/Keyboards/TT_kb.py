from aiogram.utils.keyboard import ReplyKeyboardBuilder


def tt_kb():
    tt_b = ReplyKeyboardBuilder()

    tt_b.button(text="Сегодня")
    tt_b.button(text="Завтра")

    tt_b.adjust(2)

    return tt_b.as_markup(resize_keyboard=True)
