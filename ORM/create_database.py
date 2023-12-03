import json
from datetime import datetime, timedelta

from Paths import path_base, get_faculties_and_groups, get_group_json_path
from peewee import SqliteDatabase, Model, CharField, IntegrityError, ForeignKeyField, IntegerField, DateTimeField, SQL, \
    DoesNotExist

# Определение модели
db = SqliteDatabase(path_base.db_path)


class BaseModel(Model):
    class Meta:
        database = db


class WeekType(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def initialize_week_types():
        week_types_data = ['Верхняя неделя', 'Нижняя неделя']

        for week_type_name in week_types_data:
            try:
                WeekType.create(name=week_type_name)
                print(f"Тип недели '{week_type_name}' успешно добавлен.")
            except IntegrityError:
                print(f"Тип недели '{week_type_name}' уже существует в базе данных.")

    @staticmethod
    def get_week_type_id(week_type_name):
        try:
            week_type = WeekType.get(WeekType.name == week_type_name)
            return week_type.id
        except WeekType.DoesNotExist:
            raise ValueError(f"Тип недели '{week_type_name}' не найден")


class Weekday(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def initialize_weekdays():
        weekdays_data = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

        for weekday_name in weekdays_data:
            try:
                Weekday.create(name=weekday_name)
                print(f"День недели '{weekday_name}' успешно добавлен.")
            except IntegrityError:
                print(f"День недели '{weekday_name}' уже существует в базе данных.")

    @staticmethod
    def get_weekday_id(weekday_name):
        try:
            weekday = Weekday.get(Weekday.name == weekday_name)
            return weekday.id
        except Weekday.DoesNotExist:
            raise ValueError(f"День недели '{weekday_name}' не найден")


class ClassTime(BaseModel):
    start_time = CharField(unique=True)
    end_time = CharField(unique=True)

    @staticmethod
    def initialize_class_times():
        class_times_data = [('08:30', '10:00'), ('10:10', '11:40'), ('11:50', '13:20'), ('14:00', '15:30'),
                            ('15:40', '17:10'), ('17:20', '18:50'), ('19:00', '20:30'), ('20:40', '22:10')]

        for start, end in class_times_data:
            try:
                ClassTime.create(start_time=start, end_time=end)
                print(f"Время занятия с {start} до {end} успешно добавлено.")
            except IntegrityError:
                print(f"Время занятия с {start} до {end} уже существует в базе данных.")


class LessonType(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def initialize_lesson_type():
        lesson_types = ['Лекция', 'Практическое занятие', 'Лабораторное занятие']

        for lesson_type in lesson_types:
            try:
                LessonType.create(name=lesson_type)
                print(f"Тип занятия '{lesson_type}' успешно добавлен.")
            except IntegrityError:
                print(f"Тип занятия '{lesson_type}' уже существует в базе данных.")

    @staticmethod
    def get_lesson_type_id(lesson_type_name):
        try:
            lesson_type = LessonType.get(LessonType.name == lesson_type_name)
            return lesson_type.id
        except LessonType.DoesNotExist:
            raise ValueError(f"Тип занятия '{lesson_type_name}' не найден")


class Faculty(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def add_faculty(name):
        try:
            Faculty.create(name=name)
            print(f"Факультет '{name}' успешно добавлен.")
        except IntegrityError:
            print(f"Факультет '{name}' уже существует в базе данных.")

    @staticmethod
    def get_faculty_id(faculty_name):
        try:
            faculty = Faculty.get(Faculty.name == faculty_name)
            return faculty.id
        except Faculty.DoesNotExist:
            raise ValueError(f"Факультет '{faculty_name}' не найден")

    @staticmethod
    def add_faculties_and_groups():
        faculties_and_groups = get_faculties_and_groups()

        for faculty_name, group_numbers in faculties_and_groups.items():
            Faculty.add_faculty(faculty_name)  # Добавление факультета

            for group_number in group_numbers:
                Group.add_group(group_number, faculty_name)  # Добавление группы в факультет


class Group(BaseModel):
    group_number = IntegerField(unique=True)
    faculty = ForeignKeyField(Faculty, backref='groups')

    @staticmethod
    def add_group(group_number: int, faculty_name):
        try:
            faculty = Faculty.get(Faculty.name == faculty_name)
            Group.create(group_number=group_number, faculty=faculty)
            print(f"Группа '{group_number}' успешно добавлена в факультет '{faculty_name}'.")
        except IntegrityError:
            print(f"Группа '{group_number}' уже существует в базе данных или факультет '{faculty_name}' не найден.")

    @staticmethod
    def get_group_id(group_number) -> int:
        try:
            group = Group.get(Group.group_number == group_number)
            return group.id
        except Group.DoesNotExist:
            raise ValueError(f"Группа с номером {group_number} не найдена")


class Teacher(BaseModel):
    last_name = CharField()
    first_name = CharField()
    middle_name = CharField()

    @staticmethod
    def add_teacher(last_name, first_name, middle_name):
        try:
            Teacher.create(last_name=last_name, first_name=first_name, middle_name=middle_name)
            print(f"Преподаватель {last_name} {first_name} {middle_name} успешно добавлен.")
        except IntegrityError:
            print(f"Преподаватель {last_name} {first_name} {middle_name} уже существует в базе данных.")

    @staticmethod
    def get_teacher_id(last_name, first_name, middle_name):
        try:
            teacher = Teacher.get(
                Teacher.last_name == last_name,
                Teacher.first_name == first_name,
                Teacher.middle_name == middle_name
            )
            return teacher.id
        except Teacher.DoesNotExist:
            raise ValueError(f"Преподаватель {last_name} {first_name} {middle_name} не найден")


class Subject(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def add_subject(name):
        try:
            Subject.create(name=name)
            print(f"Предмет '{name}' успешно добавлен.")
        except IntegrityError:
            print(f"Предмет '{name}' уже существует в базе данных.")

    @staticmethod
    def get_subject_id(subject_name):
        try:
            subject = Subject.get(Subject.subject_name == subject_name)
            return subject.id
        except Subject.DoesNotExist:
            raise ValueError(f"Предмет с названием {subject_name} не найден")


class Classroom(BaseModel):
    building = CharField()
    room_number = CharField(unique=True)

    @staticmethod
    def add_classroom(building, room_number):
        try:
            classroom_id = Classroom.create(building=building, room_number=room_number)
            print(f"Аудитория '{building}{room_number}' успешно добавлена.")
            return classroom_id.get_id()
        except IntegrityError:
            print(f"Аудитория '{building}{room_number}' уже существует в базе данных.")

    @staticmethod
    def get_classroom_id(building, room_number):
        try:
            classroom = Classroom.get(
                Classroom.building == building,
                Classroom.room_number == room_number
            )
            return classroom.id
        except Classroom.DoesNotExist:
            raise ValueError(f"Аудитория в корпусе {building}, номер {room_number} не найдена")


class GroupSchedule(BaseModel):
    group_id = ForeignKeyField(Group, backref='schedules')
    weekday = ForeignKeyField(Weekday, backref='schedules')
    week_type_id = ForeignKeyField(WeekType, backref='schedules')
    class_time = ForeignKeyField(ClassTime, backref='schedules')
    subject = ForeignKeyField(Subject, backref='schedules')
    lesson_type = ForeignKeyField(LessonType, backref='schedules')
    teacher = ForeignKeyField(Teacher, backref='schedules')
    classroom = ForeignKeyField(Classroom, backref='schedules')
    creation_time = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db

    @staticmethod
    def get_last_update_time(group_id):
        try:
            # Получаем последнее время обновления для группы
            last_update_time = GroupSchedule.select().where(GroupSchedule.group_id == group_id).order_by(
                GroupSchedule.creation_time.desc()).get().creation_time
            return last_update_time
        except DoesNotExist:
            return None

    @staticmethod
    def update_group_table(group_number):
        try:
            # Получаем путь к JSON-файлу для группы
            json_path = get_group_json_path(group_number)

            with open(json_path, 'r', encoding='utf-8') as file:
                schedule_data = json.load(file)

            group_id = Group.get_group_id(group_number)

            for day_data in schedule_data:
                day_name = day_data['День недели']
                day_id = Weekday.get_weekday_id(day_name)

                for pair_data in day_data['Расписание']:
                    # Извлекаем данные о паре
                    time = pair_data['Время']

                    week = pair_data['Неделя']

                    classroom_info = pair_data['Аудитория']
                    classroom_building = classroom_info["Корпус"]
                    classroom_number = classroom_info["Номер аудитории"]

                    subject_data = pair_data['Предмет']
                    teacher_data = pair_data['Преподаватель']
                    print(time, week, classroom_info, subject_data, teacher_data)

                    # Получаем или создаем записи для связанных с парой данных
                    try:
                        classroom_id = Classroom.get_classroom_id(classroom_building, classroom_number)
                    except ValueError:
                        print("Добавление нового кабинета...")
                        classroom_id = Classroom.add_classroom(classroom_building, classroom_number)
                    except Exception as e:
                        raise f"Ошибка при добавлении нового кабинета. Ошибка: {e} "

                    week_type_id = WeekType.get_week_type_id(week)
                    class_time_id = ClassTime.get_or_create_class_time_id(time)
                    subject_id = Subject.get_or_create_subject_id(subject_data)
                    lesson_type_id = LessonType.get_or_create_lesson_type_id(subject_data['Тип занятия'])
                    teacher_id = Teacher.get_or_create_teacher_id(teacher_data)

            print(f"Данные для группы {group_number} успешно обновлены.")
        except FileNotFoundError as e:
            print(f"JSON-файл для группы {group_number} не найден. Ошибка: {e}")
        except Exception as e:
            print(f"Произошла ошибка при обновлении данных для группы {group_number}: {str(e)}")

    @staticmethod
    def should_update_schedule(group_number: int):
        try:
            # Получаем идентификатор группы
            group_id = Group.get_group_id(group_number)

            # Получаем время последнего обновления таблицы
            last_update_time = GroupSchedule.get_last_update_time(group_id)

            # Если таблица не обновлялась, нужно обновить
            if last_update_time is None:
                GroupSchedule.update_group_table(group_number)
                return

            # Вычисляем разницу между текущим временем и временем последнего обновления
            time_difference = datetime.now() - last_update_time

            # Если прошло более часа, нужно обновить
            if time_difference >= timedelta(hours=1):
                GroupSchedule.update_group_table(group_number)

        except DoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
            return False


def create_tables_if_not_exist():
    tables = [WeekType, Weekday, ClassTime, LessonType, Faculty, Group, Teacher, Subject, Classroom, GroupSchedule]
    db.connect()
    db.create_tables(tables, safe=True)

    # WeekType.initialize_week_types()
    # Weekday.initialize_weekdays()
    # ClassTime.initialize_class_times()
    # LessonType.initialize_lesson_type()
    #
    # Faculty.add_faculties_and_groups()
    GroupSchedule.should_update_schedule(2251)

    db.close()


if __name__ == "__main__":
    create_tables_if_not_exist()
