from aiogram.utils.markdown import hbold
from datetime import datetime, timedelta
from ORM.schedule_information import Weekday, WeekType


def format_schedule(sorted_schedule: dict, week_type: str) -> str:
    # Форматируем данные для отправки
    formatted_schedule = f"{hbold('Неделя:')} {week_type}\n\n"

    for day, day_schedule in sorted_schedule.items():

        if week_type == WeekType.get_current_week():
            weekday = Weekday.get_weekday_id(day)
        else:
            weekday = Weekday.get_weekday_id(day) + 7

        id_current_weekday = Weekday.get_weekday_id(Weekday.get_today())

        current_weekday = datetime.today() + timedelta(days=weekday - id_current_weekday)

        formatted_schedule += (f"День недели: {hbold(day)}\n"
                               f"Дата: {hbold(current_weekday.strftime('%d.%m.%Y'))}\n\n")

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
    # def temp(pair_data):
    #     print(pair_data)
    #     pass

    # Форматируем данные для отправки
    formatted_schedule = ""

    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"День недели: {hbold(day)}\n\n"

        # Список для хранения времени пар, на которые уже выведена информация
        displayed_times = set()

        for pair_data in day_schedule:
            # temp(pair_data)
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
