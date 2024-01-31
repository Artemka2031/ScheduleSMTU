from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Middlewares.IsReg import IsRegMiddleware
from ORM.Schedule_information import GroupSchedule, Weekday, WeekType
from ORM.Users_info import User

tempRouter = Router()

tempRouter.message.middleware(IsRegMiddleware())


@tempRouter.message(F.text == "Сегодня")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    group_number = User.get_group_number(user_id)

    today = Weekday.get_today()

    if today == "Воскресенье":
        await message.answer("Сегодня выходной! 🎉")
        return

    # Получаем данные о расписании
    sorted_schedule = GroupSchedule.get_schedule(group_number, today)

    # Проверяем наличие данных
    if sorted_schedule:

        week_type = WeekType.get_current_week()
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, week_type)
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


@tempRouter.message(F.text == "Завтра")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    group_number = User.get_group_number(user_id)

    tomorrow = Weekday.get_tomorrow(Weekday.get_today())

    if tomorrow == "Воскресенье":
        await message.answer("Завтра выходной! 🎉")
        return

    # Получаем данные о расписании
    sorted_schedule = GroupSchedule.get_schedule(group_number, tomorrow)

    # Проверяем наличие данных
    if sorted_schedule:

        week_type = WeekType.get_tomorrow_week()
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, week_type)
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


def format_schedule(sorted_schedule: dict, week_type: str) -> str:
    # Форматируем данные для отправки
    formatted_schedule = f"{hbold('Неделя:')} {week_type}\n\n"

    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"День недели: {hbold(day)}\n\n"

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


def format_dual_week_schedule(sorted_schedule: dict) -> str:
    # Форматируем данные для отправки
    formatted_schedule = ""

    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"День недели: {hbold(day)}\n\n"

        # Список для хранения времени пар, на которые уже выведена информация
        displayed_times = set()

        for pair_data in day_schedule:
            pair = pair_data['Данные пары']
            week_type = pair_data['Неделя']
            pair_time = pair['Время начала']

            # Проверяем, было ли уже выведено время для данной пары
            if pair_time not in displayed_times:
                # Выводим время пары с символом 🔹
                formatted_schedule += f"🔹 {pair_time}-{pair['Время конца']}\n"
                # Добавляем время в список уже выведенных
                displayed_times.add(pair_time)

            # Пишем в какую неделю будет конкретная пара
            formatted_schedule += f"{hbold(week_type)}:\n"

            # Пишем данные о паре
            formatted_schedule += f"{pair['Наименование предмета']} "
            formatted_schedule += f"({pair['Тип занятия']})\n"

            if pair['Фамилия преподавателя']:
                formatted_schedule += f"Преподаватель: {pair['Фамилия преподавателя']}. "
                formatted_schedule += f"{pair['Имя преподавателя'][:1]}. "
                formatted_schedule += f"{pair['Отчество преподавателя'][:1]}.\n"
            formatted_schedule += f"Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n\n"

    return formatted_schedule
