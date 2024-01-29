from ORM.Schedule_information import WeekType, Weekday, ClassTime, LessonType, Faculty, Group, Teacher, Classroom, \
    Subject, GroupSchedule
from ORM.Users_info import User
from ORM.base import db


def create_tables_if_not_exist():
    tables = [WeekType, Weekday, ClassTime, LessonType, Faculty, Group, Teacher, Subject, Classroom, GroupSchedule,
              User]
    print(db.connect())
    db.create_tables(tables, safe=True)

    WeekType.initialize_week_types()
    Weekday.initialize_weekdays()
    ClassTime.initialize_class_times()
    LessonType.initialize_lesson_type()

    Faculty.add_faculties_and_groups()

    db.close()


def drop_tables():
    tables = [WeekType, Weekday, ClassTime, LessonType, Faculty, Group, Teacher, Subject, Classroom, GroupSchedule,
              User]

    with db:
        db.drop_tables(tables, safe=True)
        print("Таблицы успешно удалены.")


if __name__ == "__main__":
    drop_tables()
    create_tables_if_not_exist()
