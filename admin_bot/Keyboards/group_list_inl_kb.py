from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin_bot.RabbitMQProducer.producer_api import send_request_mq


class GroupListCallback(CallbackData, prefix="group_list"):
    group_id: int | str


async def group_list_kb(user_id, pare_time_id):
    builder = InlineKeyboardBuilder()

    users_faculty = await send_request_mq('admin_bot.tasks.get_faculty_id', [user_id])

    if not isinstance(users_faculty, int):
        print(f"Ошибка: некорректный ID факультета ({users_faculty}) для пользователя {user_id}")
        return builder.as_markup()

        # Получаем список групп, отфильтрованных по времени пары и факультету
    filtered_groups = await send_request_mq('bot.tasks.filter_groups_by_pare_time', [users_faculty, pare_time_id])

    # Проверяем, что данные получены в нужном формате (словарь {номер группы: id})
    if not isinstance(filtered_groups, dict):
        print("Ошибка: некорректный формат ответа от брокера сообщений")
        return builder.as_markup()

    for group_number, group_id in filtered_groups.items():
        builder.button(text=str(group_number), callback_data=GroupListCallback(group_id=group_id).pack())

    builder.adjust(2)

    back_button = InlineKeyboardButton(
        text='<< Назад',
        callback_data=GroupListCallback(group_id='cancel').pack()
    )

    builder.row(back_button)

    return builder.as_markup()