from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hcode
from ORM.create_database import GroupSchedule

tempRouter = Router()


@tempRouter.message(CommandStart())
async def start_messaging(message: Message) -> None:
    # Получаем данные о расписании
    sorted_schedule = GroupSchedule.get_schedule(2251, "Пятница")

    # Проверяем наличие данных
    if sorted_schedule:
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, "Нижняя неделя")
        await message.answer(f"{hbold('Расписание')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


def format_schedule(sorted_schedule: dict, week_type: str) -> str:
    # Форматируем данные для отправки
    formatted_schedule = f"{hbold('Текущая неделя:')} {week_type}:\n\n"

    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"{hbold(day)}\n"

        for pair_data in day_schedule:
            # Проверяем, соответствует ли пара запрошенной неделе
            if pair_data['Неделя'] == week_type or pair_data['Неделя'] == 'Обе недели':
                pair = pair_data['Данные пары']
                formatted_schedule += f"🔹 {pair['Время начала']}-{pair['Время конца']} "
                formatted_schedule += f"{hbold(pair['Наименование предмета'])} "
                formatted_schedule += f"({pair['Тип занятия']})\n"
                if pair['Фамилия преподавателя']:
                    formatted_schedule += f"Преподаватель: {hbold(pair['Фамилия преподавателя'])} " \
                                          f"{hbold(pair['Имя преподавателя'][:1] + '.' + pair['Отчество преподавателя'][:1])}.\n"
                formatted_schedule += f"Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n\n"

    return formatted_schedule
