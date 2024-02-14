from aiogram.utils.markdown import hbold
from datetime import datetime, timedelta

from ORM.Tables.SceduleTables.time_tables import WeekType, Weekday


def format_schedule(sorted_schedule: dict, week_type: str) -> str:
    def weekday_data(data, day_schedule):
        if data['Неделя'] == week_type or data['Неделя'] == 'Обе недели':
            pair = pair_data['Данные пары']
            day_schedule += f"🔹 {pair['Время начала']}-{pair['Время конца']} "
            day_schedule += f"{hbold(pair['Наименование предмета'])} "
            day_schedule += f"({pair['Тип занятия']})\n"
            if pair['Фамилия преподавателя']:
                day_schedule += f"Преподаватель: {hbold(pair['Фамилия преподавателя'])} " \
                                      f"{hbold(pair['Имя преподавателя'][:1] + '.' + pair['Отчество преподавателя'][:1])}.\n"
            day_schedule += f"Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n\n"
        return day_schedule

    # Форматируем данные для отправки
    formatted_schedule = f"{hbold('Неделя:')} {week_type}\n\n"

    for day, day_schedule in sorted_schedule.items():

        weekday = Weekday.get_weekday_id(day)
        this_or_next = "текущая неделя"

        if week_type != WeekType.get_current_week():
            weekday += 7
            this_or_next = "следуюшая неделя"

        id_current_weekday = Weekday.get_weekday_id(Weekday.get_today())

        current_weekday = datetime.today() + timedelta(days=weekday - id_current_weekday)

        formatted_schedule += (f"День недели: {hbold(day)}\n"
                               f"Дата: {hbold(current_weekday.strftime('%d.%m.%Y'))}, {hbold(this_or_next)}\n\n")

        for pair_data in day_schedule:
            # Проверяем, соответствует ли пара запрошенной неделе
            formatted_schedule = weekday_data(pair_data, formatted_schedule)

    return formatted_schedule


def format_dual_week_schedule(sorted_schedule: dict) -> str:
    def dual_week_data(data, format_schedule):
        pair = data['Данные пары']
        week_type = data['Неделя']
        pair_time = pair['Время начала']

        # Проверяем, было ли уже выведено время для данной пары
        if pair_time not in displayed_times:
            # Выводим время пары с символом 🔹
            format_schedule += f"🔹 {pair_time}-{pair['Время конца']}\n"
            # Добавляем время в список уже выведенных
            displayed_times.add(pair_time)

        # Пишем в какую неделю будет конкретная пара
        format_schedule += f"{hbold(week_type)}:\n"

        # Пишем данные о паре
        format_schedule += f"{pair['Наименование предмета']} "
        format_schedule += f"({pair['Тип занятия']})\n"

        if pair['Фамилия преподавателя']:
            format_schedule += f"Преподаватель: {pair['Фамилия преподавателя']}. "
            format_schedule += f"{pair['Имя преподавателя'][:1]}. "
            format_schedule += f"{pair['Отчество преподавателя'][:1]}.\n"
        format_schedule += f"Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n\n"
        return format_schedule

    # Форматируем данные для отправки
    formatted_schedule = ""

    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"День недели: {hbold(day)}\n\n"

        # Список для хранения времени пар, на которые уже выведена информация
        displayed_times = set()

        for pair_data in day_schedule:
            formatted_schedule = dual_week_data(pair_data, formatted_schedule)

    return formatted_schedule
