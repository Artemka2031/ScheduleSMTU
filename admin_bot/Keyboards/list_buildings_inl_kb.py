from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



class BuildingsListCallback(CallbackData, prefix="buildings_list"):
    building: str


def buildings_list_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text='У', callback_data=BuildingsListCallback(building='У').pack())
    builder.button(text='А', callback_data=BuildingsListCallback(building='А').pack())
    builder.button(text='Б', callback_data=BuildingsListCallback(building='Б').pack())
    builder.button(text='Г', callback_data=BuildingsListCallback(building='Г').pack())
    builder.adjust(2)

    m_btn = InlineKeyboardButton(text='М', callback_data=BuildingsListCallback(building='М').pack())
    builder.row(m_btn)

    back_button = InlineKeyboardButton(
        text='<< Назад',
        callback_data=BuildingsListCallback(building='cancel').pack()
    )

    # Добавляем кнопку "Назад" на отдельную строку
    builder.row(back_button)

    return builder.as_markup()