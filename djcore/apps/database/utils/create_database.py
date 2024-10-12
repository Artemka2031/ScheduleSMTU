import asyncio
import os
import subprocess
from djcore.apps.database.utils.SceduleTables import GroupSchedule
from djcore.apps.database.utils.SceduleTables import Faculty, Department, Group, Teacher, TeacherDepartment
from djcore.apps.database.utils.SceduleTables import LessonType, Subject, Classroom
from djcore.apps.database.utils.SceduleTables.time_tables import WeekType, Weekday, ClassTime
from djcore.apps.database.utils.UserTables import Notification
from djcore.apps.database.utils.UserTables.suggestion_table import Suggestion
from djcore.apps.database.utils.UserTables.user_table import User
from ORM.database_declaration_and_exceptions import db
from djcore.apps.database.utils.Path.schedule_path_functions import get_all_group_numbers
from djcore.apps.database.utils.Path.path_base import path_base  # Путь к папке для резервных копий
from datetime import datetime


async def create_tables_if_not_exist():
    """
    Создает все таблицы в базе данных и инициализирует их содержимое.
    """
    tables = [WeekType, Weekday, ClassTime,
              Faculty, Department, Group, Teacher, TeacherDepartment,
              LessonType, Subject, Classroom,
              GroupSchedule,
              User, Suggestion, Notification]

    db.create_tables(tables, safe=True)

    WeekType.initialize_week_types()
    Weekday.initialize_weekdays()
    ClassTime.initialize_class_times()
    LessonType.initialize_lesson_type()

    db.close()


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


def clear_schedule_tables():
    """
    Очищает только таблицы, связанные с расписанием, временно отключая проверки внешних ключей,
    используя TRUNCATE для сброса данных и индексов.
    """
    schedule_tables = [
        GroupSchedule,
        TeacherDepartment,
        Teacher,
        Subject,
        Classroom,
        LessonType,
        WeekType,
        Weekday,
        ClassTime
    ]

    with db.atomic():
        try:
            # Отключаем проверку внешних ключей
            db.execute_sql('SET foreign_key_checks = 0;')

            # Очищаем каждую таблицу, связанную с расписанием
            for table in schedule_tables:
                table.truncate_table()
                print(f"Таблица {table.__name__} успешно очищена.")

            print("Таблицы с расписанием успешно очищены.")
        finally:
            # Включаем проверку внешних ключей
            db.execute_sql('SET foreign_key_checks = 1;')


async def refresh_database():
    """
    Создает резервную копию, очищает таблицы с расписанием и заново создает их, затем синхронизирует данные.
    """
    # Шаг 1: Создание резервной копии
    backup_database()

    # Шаг 2: Очистка таблиц с расписанием
    clear_schedule_tables()

    # Шаг 3: Пересоздание таблиц
    await create_tables_if_not_exist()

    # Шаг 4: Синхронизация данных после парсинга
    Faculty.add_faculties_and_groups()

    groups = get_all_group_numbers()
    for group in groups:
        GroupSchedule.set_schedule(group, forced_update=False)

    TeacherDepartment.set_teachers_department()

    print("База данных успешно обновлена и синхронизирована.")


if __name__ == "__main__":
    asyncio.run(refresh_database())
