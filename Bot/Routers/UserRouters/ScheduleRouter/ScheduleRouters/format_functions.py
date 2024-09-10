from aiogram.utils.markdown import hbold


def format_schedule(sorted_schedule: dict, week_type: str) -> str:
    def weekday_data(data, day_schedule):
        if data['Неделя'] == week_type or data['Неделя'] == 'Обе недели':
            pair = data['Данные пары']
            day_schedule += f"🔹 {pair['Время начала']}-{pair['Время конца']} — {hbold(pair['Наименование предмета'])} "
            day_schedule += f"({pair['Тип занятия']})\n"
            if pair['Фамилия преподавателя']:
                day_schedule += f"👨‍🏫 Преподаватель: {hbold(pair['Фамилия преподавателя'])} " \
                                f"{hbold(pair['Имя преподавателя'][:1] + '.' + pair['Отчество преподавателя'][:1])}.\n"
            day_schedule += f"🏫 Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n"
            if pair['Группы']:
                day_schedule += f"👥 Другие группы: {', '.join(map(str, pair['Группы']))}\n"
            day_schedule += "—" * 20 + "\n"
        return day_schedule

    formatted_schedule = f"{hbold('Неделя:')} {week_type}\n\n"
    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"📅 {hbold(day)}:\n\n"
        for pair_data in day_schedule:
            formatted_schedule = weekday_data(pair_data, formatted_schedule)

    return formatted_schedule


def format_dual_week_schedule(sorted_schedule: dict) -> str:
    def dual_week_data(data, format_schedule):
        pair = data['Данные пары']
        week_type = data['Неделя']
        pair_time = pair['Время начала']

        if pair_time not in displayed_times:
            format_schedule += f"🔹 {pair_time}-{pair['Время конца']}\n"
            displayed_times.add(pair_time)

        format_schedule += f"{hbold(week_type)}:\n"
        format_schedule += f"{hbold(pair['Наименование предмета'])} "
        format_schedule += f"({pair['Тип занятия']})\n"
        if pair['Фамилия преподавателя']:
            format_schedule += f"👨‍🏫 Преподаватель: {pair['Фамилия преподавателя']} " \
                               f"{pair['Имя преподавателя'][:1]}. {pair['Отчество преподавателя'][:1]}.\n"
        format_schedule += f"🏫 Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n"
        if pair['Группы']:
            format_schedule += f"👥 Другие группы: {', '.join(map(str, pair['Группы']))}\n"
        format_schedule += "—" * 20 + "\n"
        return format_schedule

    formatted_schedule = ""
    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"📅 {hbold(day)}:\n\n"
        displayed_times = set()
        for pair_data in day_schedule:
            formatted_schedule = dual_week_data(pair_data, formatted_schedule)

    return formatted_schedule


def format_teacher_schedule(sorted_schedule: dict, week_type: str) -> str:
    def weekday_data(data, day_schedule):
        if data['Неделя'] == week_type or data['Неделя'] == 'Обе недели':
            pair = data['Данные пары']
            day_schedule += f"🔹 {pair['Время начала']}-{pair['Время конца']} — {hbold(pair['Наименование предмета'])} "
            day_schedule += f"({pair['Тип занятия']})\n"
            day_schedule += f"👥 Группы: {', '.join(map(str, pair['Группы']))}\n"
            day_schedule += f"🏫 Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n"
            day_schedule += "—" * 20 + "\n"
        return day_schedule

    formatted_schedule = f"{hbold('Неделя:')} {week_type}\n\n"
    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"📅 {hbold(day)}:\n\n"
        for pair_data in day_schedule:
            formatted_schedule = weekday_data(pair_data, formatted_schedule)

    return formatted_schedule


def format_teacher_dual_week_schedule(sorted_schedule: dict) -> str:
    def dual_week_data(data, format_schedule):
        pair = data['Данные пары']
        week_type = data['Неделя']
        pair_time = pair['Время начала']

        if pair_time not in displayed_times:
            format_schedule += f"🔹 {pair_time}-{pair['Время конца']}\n"
            displayed_times.add(pair_time)

        format_schedule += f"{hbold(week_type)}:\n"
        format_schedule += f"{hbold(pair['Наименование предмета'])} "
        format_schedule += f"({pair['Тип занятия']})\n"
        format_schedule += f"👥 Группы: {', '.join(map(str, pair['Группы']))}\n"
        format_schedule += f"🏫 Аудитория: {pair['Корпус']} {pair['Номер аудитории']}\n"
        format_schedule += "—" * 20 + "\n"

        return format_schedule

    formatted_schedule = ""
    for day, day_schedule in sorted_schedule.items():
        formatted_schedule += f"📅 {hbold(day)}:\n\n"
        displayed_times = set()
        for pair_data in day_schedule:
            formatted_schedule = dual_week_data(pair_data, formatted_schedule)

    return formatted_schedule
