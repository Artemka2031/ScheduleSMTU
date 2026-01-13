from djcore.apps.database.utils.ScheduleTables.time_tables import Weekday, WeekType, ClassTime
from djcore.apps.database.utils.ScheduleTables.group_schedule import GroupSchedule
from djcore.apps.database.utils.ScheduleTables.group_tables import Faculty, TeacherDepartment
from djcore.apps.database.utils.ScheduleTables.subject_tables import LessonType

from djcore.apps.database.utils.Path.schedule_path_functions import get_all_group_numbers


def refresh_database():
    """
    Создает резервную копию, очищает таблицы с расписанием и заново создает их, затем синхронизирует данные.
    """

    # Шаг 4: Синхронизация данных после парсинга
    Faculty.add_faculties_and_groups()
    Weekday.initialize_weekdays()
    WeekType.initialize_week_types()
    ClassTime.initialize_class_times()
    LessonType.initialize_lesson_type()
    groups = get_all_group_numbers()
    for group in groups:
        GroupSchedule.set_schedule(group, forced_update=False)

    TeacherDepartment.set_teachers_department()

    print("База данных успешно обновлена и синхронизирована.")

