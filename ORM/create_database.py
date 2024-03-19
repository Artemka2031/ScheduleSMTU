from ORM.Tables.SceduleTables.group_schedule import GroupSchedule
from ORM.Tables.SceduleTables.group_tables import Faculty, Department, Group, Teacher, TeacherDepartment
from ORM.Tables.SceduleTables.subject_tables import LessonType, Subject, Classroom
from ORM.Tables.SceduleTables.time_tables import WeekType, Weekday, ClassTime
from ORM.Tables.UserTables.notification_table import Notification
from ORM.Tables.UserTables.suggestion_table import User, Suggestion
from ORM.database_declaration_and_exceptions import db
from Path.schedule_path_functions import get_all_group_numbers


def create_tables_if_not_exist():
    # tables = [WeekType, Weekday, ClassTime,
    #           Faculty, Department, Group, Teacher, TeacherDepartment,
    #           LessonType, Subject, Classroom,
    #           GroupSchedule,
    #           User, Suggestion, Notification]
    tables = [Notification]

    db.create_tables(tables, safe=True)

    # WeekType.initialize_week_types()
    # Weekday.initialize_weekdays()
    # ClassTime.initialize_class_times()
    # LessonType.initialize_lesson_type()

    db.close()


def drop_tables():
    tables = [Suggestion]

    with db:
        db.drop_tables(tables, safe=True)
        print("Таблицы успешно удалены.")


def refresh_database():
    Faculty.add_faculties_and_groups()

    groups = get_all_group_numbers()
    for group in groups:
        GroupSchedule.set_schedule(group, forced_update=False)

    TeacherDepartment.set_teachers_department()


if __name__ == "__main__":
    create_tables_if_not_exist()
