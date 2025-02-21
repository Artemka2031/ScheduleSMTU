import os

from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcore.settings")  # замените your_project.settings на ваш модуль настроек
import django
django.setup()

import asyncio
import subprocess
from djcore.apps.database.utils.ScheduleTables.time_tables import Weekday, WeekType, ClassTime
from djcore.apps.database.utils.ScheduleTables.group_schedule import GroupSchedule
from djcore.apps.database.utils.ScheduleTables.group_tables import Faculty, Department, Group, Teacher, TeacherDepartment
from djcore.apps.database.utils.ScheduleTables.subject_tables import LessonType, Subject, ClassRoom
# from djcore.apps.database.utils.UserTables.notification_table import Notification
# from djcore.apps.database.utils.UserTables.suggestion_table import Suggestion
# from djcore.apps.database.utils.UserTables.user_table import User
from djcore.apps.database.utils.Path.schedule_path_functions import get_all_group_numbers
from djcore.apps.database.utils.Path.path_base import path_base  # Путь к папке для резервных копий
from datetime import datetime

# async def create_tables_if_not_exist():
#     """
#     Создает все таблицы в базе данных и инициализирует их содержимое.
#     """
#     tables = [WeekType, Weekday, ClassTime,
#               Faculty, Department, Group, Teacher, TeacherDepartment,
#               LessonType, Subject, ClassRoom,
#               GroupSchedule,
#               User, Suggestion, Notification]
#
#     db.create_tables(tables, safe=True)
#
#     WeekType.initialize_week_types()
#     Weekday.initialize_weekdays()
#     ClassTime.initialize_class_times()
#     LessonType.initialize_lesson_type()
#
#     db.close()


def backup_database():
    """
    Создает дамп базы данных в SQL-файл с использованием mysqldump и сохраняет его в указанной папке.
    """
    # Формируем путь и имя для резервного файла
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file_path = os.path.join(path_base.db_backups, f"backup_{timestamp}.sql")

    # Параметры подключения к базе данных
    db_name = 'schedule'
    user = 'schedule_SMTU'
    password = 'wD7jQ#2zRt!vY6Tp'
    host = 'localhost'

    # Выполнение mysqldump для создания резервной копии базы данных
    try:
        command = f"mysqldump -u {user} -p{password} -h {host} {db_name} > {backup_file_path}"
        subprocess.run(command, shell=True, check=True)
        print(f"Резервная копия базы данных создана: {backup_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании резервной копии базы данных: {e}")

    return backup_file_path


# def clear_schedule_tables():
#     """
#     Очищает только таблицы, связанные с расписанием, временно отключая проверки внешних ключей,
#     используя TRUNCATE для сброса данных и индексов.
#     """
#     schedule_tables = [
#         GroupSchedule,
#         TeacherDepartment,
#         Teacher,
#         Subject,
#         ClassRoom,
#         LessonType,
#         WeekType,
#         Weekday,
#         ClassTime
#     ]
#
#     with db.atomic():
#         try:
#             # Отключаем проверку внешних ключей
#             db.execute_sql('SET foreign_key_checks = 0;')
#
#             # Очищаем каждую таблицу, связанную с расписанием
#             for table in schedule_tables:
#                 table.truncate_table()
#                 print(f"Таблица {table.__name__} успешно очищена.")
#
#             print("Таблицы с расписанием успешно очищены.")
#         finally:
#             # Включаем проверку внешних ключей
#             db.execute_sql('SET foreign_key_checks = 1;')


async def refresh_database():
    """
    Создает резервную копию, очищает таблицы с расписанием и заново создает их, затем синхронизирует данные.
    """
    # Шаг 1: Создание резервной копии
    # backup_database()

    # Шаг 2: Очистка таблиц с расписанием
    # clear_schedule_tables()
    #
    # # Шаг 3: Пересоздание таблиц
    # await create_tables_if_not_exist()

    # Шаг 4: Синхронизация данных после парсинга
    await sync_to_async(Faculty.add_faculties_and_groups)()
    await sync_to_async(Weekday.initialize_weekdays)()
    await sync_to_async(WeekType.initialize_week_types)()
    await sync_to_async(ClassTime.initialize_class_times)()
    await sync_to_async(LessonType.initialize_lesson_type)()
    groups = get_all_group_numbers()
    for group in groups:
        await sync_to_async(GroupSchedule.set_schedule)(group, forced_update=False)

    await sync_to_async(TeacherDepartment.set_teachers_department)()

    print("База данных успешно обновлена и синхронизирована.")

#
# if __name__ == "__main__":
#     asyncio.run(refresh_database())
