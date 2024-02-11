import json
from datetime import datetime, timedelta

from typing import List, Dict, Optional

import pytz
from peewee import CharField, IntegrityError, ForeignKeyField, IntegerField, DateTimeField, SQL, \
    DoesNotExist

from ORM.database_declaration_and_exceptions import BaseModel, DataBaseException, moscow_tz
from Parsing.group_parser import load_group_from_site
from Paths import get_faculties_and_groups, get_group_json_path


class WeekType(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def initialize_week_types():
        week_types_data = ['Верхняя неделя', 'Нижняя неделя', 'Обе недели']

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
        except DoesNotExist:
            raise ValueError(f"Тип недели '{week_type_name}' не найден")

    @staticmethod
    def get_current_week():
        week_number = datetime.now(moscow_tz).isocalendar()[1]
        return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'

    @staticmethod
    def get_tomorrow_week():
        tomorrow_date = datetime.now(moscow_tz) + timedelta(days=1)
        week_number = tomorrow_date.isocalendar()[1]
        return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'


class Weekday(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def initialize_weekdays():
        weekdays_data = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

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
        except DoesNotExist:
            raise ValueError(f"День недели '{weekday_name}' не найден")

    @staticmethod
    def get_order(day_name: str) -> int:
        # Ваш код для определения порядка дня недели
        order = {
            'Понедельник': 1,
            'Вторник': 2,
            'Среда': 3,
            'Четверг': 4,
            'Пятница': 5,
            'Суббота': 6
        }

        # Вернуть порядок текущего дня
        return order.get(day_name, 0)

    @staticmethod
    def get_today():
        current_date = datetime.now(moscow_tz)
        try:
            today_weekday = Weekday.get(id=current_date.weekday() + 1)
            return today_weekday.name
        except DoesNotExist:
            raise ValueError(f"Ошибка при определении сегодняшнего дня")

    @staticmethod
    def get_tomorrow(current_weekday_name):
        try:
            current_weekday = Weekday.get(Weekday.name == current_weekday_name)
            tomorrow_id = (current_weekday.id % 7) + 1
            tomorrow_weekday = Weekday.get(id=tomorrow_id)
            return tomorrow_weekday.name
        except DoesNotExist:
            raise ValueError(f"Ошибка при определении завтрашнего дня")


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

    @staticmethod
    def get_class_time_id(time_range):
        start_time, end_time = map(lambda x: x.strip(), time_range.split('-'))

        try:
            class_time = ClassTime.get(start_time=start_time, end_time=end_time)
        except DoesNotExist:
            raise ValueError(
                f"Время занятия с {start_time} до {end_time} не было добавлено при инициализации либо недопустимо.")

        return class_time.id


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
        except DoesNotExist:
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
        except DoesNotExist:
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
        except DoesNotExist:
            raise ValueError(f"Группа с номером {group_number} не найдена")


class Teacher(BaseModel):
    last_name = CharField()
    first_name = CharField()
    middle_name = CharField()

    @staticmethod
    def add_teacher(last_name, first_name, middle_name):
        try:
            teacher = Teacher.create(last_name=last_name, first_name=first_name, middle_name=middle_name)
            print(f"Преподаватель {last_name} {first_name} {middle_name} успешно добавлен.")
            return teacher.get_id()
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
        except DoesNotExist:
            raise ValueError(f"Преподаватель {last_name} {first_name} {middle_name} не найден")


class Subject(BaseModel):
    name = CharField(unique=True)

    @staticmethod
    def add_subject(name):
        try:
            subject = Subject.create(name=name)
            print(f"Предмет '{name}' успешно добавлен.")
            return subject.get_id()
        except IntegrityError:
            print(f"Предмет '{name}' уже существует в базе данных.")

    @staticmethod
    def get_subject_id(subject_name):
        try:
            subject = Subject.get(Subject.name == subject_name)
            return subject.id
        except Exception as e:
            raise ValueError(f"Предмет с названием {subject_name} не найден: {str(e)}")


class Classroom(BaseModel):
    building = CharField()
    room_number = CharField()

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
        except DoesNotExist:
            raise ValueError(f"Аудитория в корпусе {building}, номер {room_number} не найдена")


class GroupSchedule(BaseModel):
    group_id = ForeignKeyField(Group, backref='schedules')
    day_id = ForeignKeyField(Weekday, backref='schedules')
    week_type_id = ForeignKeyField(WeekType, backref='schedules')
    class_time_id = ForeignKeyField(ClassTime, backref='schedules')
    subject_id = ForeignKeyField(Subject, backref='schedules')
    lesson_type_id = ForeignKeyField(LessonType, backref='schedules')
    teacher_id = ForeignKeyField(Teacher, backref='schedules')
    classroom_id = ForeignKeyField(Classroom, backref='schedules')
    creation_time = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    @staticmethod
    def get_last_update_time(group_id):
        try:
            # Получаем последнее время обновления для группы
            last_update_time_str = GroupSchedule.select().where(
                GroupSchedule.group_id == group_id
            ).order_by(
                GroupSchedule.creation_time.desc()
            ).get().creation_time

            # Преобразуем строку в объект datetime с учетом временной зоны
            last_update_time_moscow = datetime.fromisoformat(last_update_time_str)
            last_update_time_moscow = last_update_time_moscow.replace(tzinfo=pytz.timezone('Europe/Moscow'))

            return last_update_time_moscow
        except DoesNotExist:
            return None

    @staticmethod
    def update_group_table(group_number):
        try:
            # Загружаем данные с сайта
            load_group_from_site(group_number)

            # Получаем путь к JSON-файлу для группы
            json_path = get_group_json_path(group_number)

            with open(json_path, 'r', encoding='utf-8') as file:
                schedule_data = json.load(file)

            group_id = Group.get_group_id(group_number)

            option = ""
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
                    subject_name = subject_data['Наименование предмета']
                    subject_type = subject_data['Тип занятия']
                    teacher_data = pair_data['Преподаватель']

                    teacher_last_name = teacher_data['Фамилия']
                    teacher_first_name = teacher_data['Имя']
                    teacher_middle_name = teacher_data['Отчество']

                    # Получаем или создаем записи для связанных с парой данных
                    try:
                        classroom_id = Classroom.get_classroom_id(classroom_building, classroom_number)
                    except ValueError:
                        classroom_id = Classroom.add_classroom(classroom_building, classroom_number)
                    except DataBaseException as e:
                        raise f"Ошибка при добавлении нового кабинета: {str(e)} "

                    try:
                        week_type_id = WeekType.get_week_type_id(week)
                    except ValueError as e:
                        raise ValueError(f"Неизвестный тип недели. Ошибка: {e}")
                    except DataBaseException as e:
                        raise f"Ошибка при чтении id типа недели: {e}"

                    try:
                        class_time_id = ClassTime.get_class_time_id(time)
                    except ValueError as e:
                        raise ValueError(f"Неизвестное время занятий. Ошибка: {e}")
                    except DataBaseException as e:
                        raise f"Ошибка при чтении id типа недели: {e}"

                    try:
                        subject_id = Subject.get_subject_id(subject_name)
                    except ValueError:
                        subject_id = Subject.add_subject(subject_name)
                    except DataBaseException as e:
                        raise f"Ошибка при добавлении предмета: {e}"

                    try:
                        lesson_type_id = LessonType.get_lesson_type_id(subject_type)
                    except ValueError as e:
                        raise ValueError(f"Неизвестное тип занятий. Ошибка: {e}")
                    except DataBaseException as e:
                        raise f"Ошибка при чтении типа предмета: {e}"

                    try:
                        teacher_id = Teacher.get_teacher_id(teacher_last_name, teacher_first_name, teacher_middle_name)
                    except ValueError:
                        teacher_id = Teacher.add_teacher(teacher_last_name, teacher_first_name, teacher_middle_name)
                    except DataBaseException as e:
                        raise f"Ошибка при чтении id преподавателя: {e}"

                    # Проверяем, существует ли запись для данного дня, времени и группы
                    try:
                        pair_record = GroupSchedule.get(
                            day_id=day_id,
                            group_id=group_id,
                            class_time_id=class_time_id,
                            week_type_id=week_type_id
                        )
                        # Если запись существует, обновляем ее
                        pair_record.classroom_id = classroom_id
                        pair_record.subject_id = subject_id
                        pair_record.lesson_type_id = lesson_type_id
                        pair_record.teacher_id = teacher_id
                        pair_record.creation_time = datetime.now(moscow_tz)
                        pair_record.save()

                        option = "update"
                    except DoesNotExist:
                        # Если записи нет, создаем новую запись
                        GroupSchedule.create(
                            day_id=day_id,
                            group_id=group_id,
                            class_time_id=class_time_id,
                            week_type_id=week_type_id,
                            classroom_id=classroom_id,
                            subject_id=subject_id,
                            lesson_type_id=lesson_type_id,
                            teacher_id=teacher_id,
                            creation_time=datetime.now(moscow_tz)
                        )

                        option = "create"

            if option == "create":
                message = f"Данные для группы {group_number} успешно добавлены."
            else:
                message = f"Данные для группы {group_number} успешно обновлены."

            print(message)

        except FileNotFoundError as e:
            print(f"JSON-файл для группы {group_number} не найден. Ошибка: {e}")
        except Exception as e:
            print(f"Произошла ошибка при обновлении данных для группы {group_number}: {str(e)}")

    @staticmethod
    def set_schedule(group_number: int):
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
            time_difference = datetime.now(moscow_tz) - last_update_time

            # Если прошло более часа, нужно обновить
            if time_difference >= timedelta(hours=5):
                GroupSchedule.update_group_table(group_number)

        except DoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
            return False

    @staticmethod
    def get_schedule(group_number: int, current_day: Optional[str] = None) -> Dict[str, List[Dict]]:
        try:
            GroupSchedule.set_schedule(group_number)

            # Get the group id
            group_id = Group.get_group_id(group_number)

            # Perform a query to get the schedule with JOIN for related tables
            schedule_data = (GroupSchedule
                             .select(GroupSchedule, Weekday, ClassTime, WeekType, Classroom, Subject, LessonType,
                                     Teacher)
                             .join(Weekday)
                             .switch(GroupSchedule)
                             .join(ClassTime)
                             .switch(GroupSchedule)
                             .join(WeekType)
                             .switch(GroupSchedule)
                             .join(Classroom)
                             .switch(GroupSchedule)
                             .join(Subject)
                             .switch(GroupSchedule)
                             .join(LessonType)
                             .switch(GroupSchedule)
                             .join(Teacher)
                             .where(GroupSchedule.group_id == group_id))

            # Transform the query result into a structured format
            schedule = {}
            for record in schedule_data:
                day_name = record.day_id.name
                start_class_time = record.class_time_id.start_time
                end_class_time = record.class_time_id.end_time
                classroom_building = record.classroom_id.building
                classroom_number = record.classroom_id.room_number
                subject_name = record.subject_id.name
                lesson_type = record.lesson_type_id.name
                teacher_last_name = record.teacher_id.last_name
                teacher_first_name = record.teacher_id.first_name
                teacher_middle_name = record.teacher_id.middle_name
                week_type = record.week_type_id.name

                # Создаем данные для пары
                pair_data = {
                    'Время начала': start_class_time,
                    'Время конца': end_class_time,
                    'Корпус': classroom_building,
                    'Номер аудитории': classroom_number,
                    'Наименование предмета': subject_name,
                    'Тип занятия': lesson_type,
                    'Фамилия преподавателя': teacher_last_name,
                    'Имя преподавателя': teacher_first_name,
                    'Отчество преподавателя': teacher_middle_name,
                }

                # Добавляем пару в расписание
                if day_name not in schedule:
                    schedule[day_name] = []

                schedule[day_name].append({'Неделя': week_type, 'Данные пары': pair_data})

            # Если указан текущий день, фильтруем расписание
            if current_day:
                schedule = {current_day: schedule.get(current_day, [])}

            # Сортируем дни недели
            sorted_schedule = dict(sorted(schedule.items(), key=lambda x: Weekday.get_order(x[0])))

            # Сортируем пары внутри каждого дня недели по времени начала
            for day_schedule in sorted_schedule.values():
                day_schedule.sort(key=lambda x: datetime.strptime(x['Данные пары']['Время начала'], '%H:%M'))

            return sorted_schedule

        except DoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
            return {}
        except Exception as e:
            print(f"Произошла ошибка при получении расписания для группы {group_number}: {str(e)}")
            return {}
