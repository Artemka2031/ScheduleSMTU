import json
from datetime import datetime, timedelta

from typing import List, Dict, Optional

import pytz
from peewee import ForeignKeyField, DateTimeField, SQL, \
    DoesNotExist

from ORM.Tables.SceduleTables.group_tables import Group
from ORM.Tables.SceduleTables.subject_tables import Subject, Classroom, Teacher, LessonType
from ORM.Tables.SceduleTables.time_tables import Weekday, ClassTime, WeekType
from ORM.database_declaration_and_exceptions import BaseModel, DataBaseException, moscow_tz
from Parsing.Parsers.ScheduleParsing.SubParsers.group_parser import load_group_sync
from Path.schedule_path_functions import get_group_json_path_sync


class GroupSchedule(BaseModel):
    """
        A class to manage the schedule of groups within an educational institution asynchronously.

        Attributes:
            group_id (ForeignKeyField): Reference to the group this schedule belongs to.
            day_id (ForeignKeyField): Reference to the weekday of the schedule.
            week_type_id (ForeignKeyField): Reference to the week type (e.g., odd or even week).
            class_time_id (ForeignKeyField): Reference to the class time slot.
            subject_id (ForeignKeyField): Reference to the subject being taught.
            lesson_type_id (ForeignKeyField): Reference to the type of lesson (e.g., lecture, lab).
            teacher_id (ForeignKeyField): Reference to the teacher.
            classroom_id (ForeignKeyField): Reference to the classroom.
            creation_time (DateTimeField): Timestamp of when the schedule entry was created or last updated.
    """
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
        """
            Asynchronously retrieves the last update time of the schedule for a specified group.

            Params:
                group_id (int): The ID of the group to retrieve the last update time for.

            Returns:
                Optional[datetime]: The last update time of the schedule or None if not found.
        """
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
    def update_group_table(group_number: int, forced_update: bool = True):
        """
            Asynchronously updates the schedule table for a specified group by loading data from an external source.

            Params:
                group_number (int): The number of the group to update the schedule for.
        """
        try:
            if forced_update:
                # Загружаем данные с сайта
                load_group_sync(group_number)

            # Получаем путь к JSON-файлу для группы
            json_path = get_group_json_path_sync(group_number)

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
    def set_schedule(group_number: int, forced_update: bool = True):
        """
            Synchronously sets the schedule for a specified group, updating it if necessary.

            Params:
                group_number (int): The number of the group to set the schedule for.

            Returns:
                bool: True if the operation was successful, False otherwise.
        """
        try:
            # Получаем идентификатор группы
            group_id = Group.get_group_id(group_number)
            # Получаем время последнего обновления таблицы
            last_update_time = GroupSchedule.get_last_update_time(group_id)

            # Если таблица не обновлялась, нужно обновить
            if last_update_time is None:
                GroupSchedule.update_group_table(group_number, forced_update=forced_update)
                return

            # Вычисляем разницу между текущим временем и временем последнего обновления
            time_difference = datetime.now(moscow_tz) - last_update_time

            # Если прошло более 23 часов, нужно обновить
            if time_difference >= timedelta(hours=23):
                GroupSchedule.update_group_table(group_number, forced_update=forced_update)

        except DoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
            return False

    @staticmethod
    def get_schedule(group_number: int, current_day: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
            Asynchronously retrieves the schedule for a specified group, optionally filtered by the current day.

            Params:
                group_number (int): The number of the group to retrieve the schedule for.
                current_day (Optional[str]): If specified, filters the schedule to only include this day.

            Returns:
                Dict[str, List[Dict]]: The schedule for the group, structured by day.
        """
        try:

            group_number = int(group_number)

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
