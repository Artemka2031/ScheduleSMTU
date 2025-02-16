import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import pytz
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from djcore.apps.database.utils.send_response import send_response
from djcore.apps.parser.utils.Parsers.ScheduleParsing.SubParsers.group_parser import load_group_sync
from djcore.apps.database.utils.Path.schedule_path_functions import get_group_json_path_sync
from djcore.apps.database.utils.ScheduleTables.group_tables import Group, Teacher
from djcore.apps.database.utils.ScheduleTables.subject_tables import Subject, LessonType, ClassRoom
from djcore.apps.database.utils.ScheduleTables.time_tables import Weekday, WeekType, ClassTime
from djcore.apps.database.utils.config_db import moscow_tz
from djcore.celery_app import app

class GroupSchedule(models.Model):
    group = models.ForeignKey(Group, models.DO_NOTHING)
    day = models.ForeignKey(Weekday, models.DO_NOTHING)
    week_type = models.ForeignKey(WeekType, models.DO_NOTHING)
    class_time = models.ForeignKey(ClassTime, models.DO_NOTHING)
    subject = models.ForeignKey(Subject, models.DO_NOTHING)
    lesson_type = models.ForeignKey(LessonType, models.DO_NOTHING)
    teacher = models.ForeignKey(Teacher, models.DO_NOTHING)
    classroom = models.ForeignKey(ClassRoom, models.DO_NOTHING)
    creation_time = models.DateTimeField()
    objects = models.Manager()

    class Meta:
        db_table = 'groupschedule'

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
            last_update_time_obj = GroupSchedule.objects.filter(group_id=group_id).order_by('-creation_time').first()

            if last_update_time_obj is not None:
                last_update_time_obj = last_update_time_obj.creation_time

                # Преобразуем объект datetime в строку, если необходимо
                if isinstance(last_update_time_obj, datetime):
                    last_update_time_str = last_update_time_obj.isoformat()
                elif isinstance(last_update_time_obj, str):
                    last_update_time_str = last_update_time_obj
                else:
                    print("Неподдерживаемый тип времени обновления.")
                    last_update_time_str = None
            else:
                print("Не найдено ни одной записи для данной группы.")
                last_update_time_str = None

            # Преобразуем строку в объект datetime с учетом временной зоны
            last_update_time_moscow = datetime.fromisoformat(last_update_time_str)
            last_update_time_moscow = last_update_time_moscow.replace(tzinfo=pytz.timezone('Europe/Moscow'))

            return last_update_time_moscow
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(f"Произошла ошибка при получении времени последнего обновления: {e}")
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
                        classroom_id = ClassRoom.get_classroom_id(classroom_building, classroom_number)
                    except ValueError:
                        classroom_id = ClassRoom.add_classroom(classroom_building, classroom_number)
                    except Exception as e:
                        raise f"Ошибка при добавлении нового кабинета: {str(e)} "

                    try:
                        week_type_id = WeekType.get_week_type_id(week)
                    except ValueError as e:
                        raise ValueError(f"Неизвестный тип недели. Ошибка: {e}")
                    except Exception as e:
                        raise f"Ошибка при чтении id типа недели: {e}"

                    try:
                        class_time_id = ClassTime.get_class_time_id(time)
                    except ValueError as e:
                        raise ValueError(f"Неизвестное время занятий. Ошибка: {e}")
                    except Exception as e:
                        raise f"Ошибка при чтении id типа недели: {e}"

                    try:
                        subject_id = Subject.get_subject_id(subject_name)
                    except ValueError:
                        subject_id = Subject.add_subject(subject_name)
                    except Exception as e:
                        raise f"Ошибка при добавлении предмета: {e}"

                    try:
                        lesson_type_id = LessonType.get_lesson_type_id(subject_type)
                    except ValueError as e:
                        raise ValueError(f"Неизвестное тип занятий. Ошибка: {e}")
                    except Exception as e:
                        raise f"Ошибка при чтении типа предмета: {e}"

                    try:
                        teacher_id = Teacher.get_teacher_id(teacher_last_name, teacher_first_name, teacher_middle_name)
                    except ValueError:
                        teacher_id = Teacher.add_teacher(teacher_last_name, teacher_first_name, teacher_middle_name)
                    except Exception as e:
                        raise f"Ошибка при чтении id преподавателя: {e}"

                    # Проверяем, существует ли запись для данного дня, времени и группы
                    try:
                        pair_record = GroupSchedule.objects.get(
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
                    except ObjectDoesNotExist:
                        # Если записи нет, создаем новую запись
                        GroupSchedule.objects.create(
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
            group_id = Group.objects.get(group_number=group_number)
            # Получаем время последнего обновления таблицы
            last_update_time = GroupSchedule.get_last_update_time(group_id)

            # Если таблица не обновлялась, нужно обновить
            if last_update_time is None:
                GroupSchedule.update_group_table(group_number, forced_update=forced_update)
                return

            # Вычисляем разницу между текущим временем и временем последнего обновления
            time_difference = datetime.now(moscow_tz) - last_update_time

            # Если прошло более 23 часов, нужно обновить
            if time_difference >= timedelta(hours=1):
                GroupSchedule.update_group_table(group_number, forced_update=forced_update)

        except ObjectDoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
            return False

    @staticmethod
    @app.task(name='bot.tasks.get_schedule_teacher')
    def get_schedule_teacher(teacher_id: int, current_day: Optional[str] = None, reply_to = None, correlation_id = None):
        """
        Retrieves the schedule for a specified teacher, optionally filtered by the current day.

        Params:
            teacher_id (int): The ID of the teacher to retrieve the schedule for.
            current_day (Optional[str]): If specified, filters the schedule to only include this day.

        Returns:
            Dict[str, List[Dict]]: The schedule for the teacher, structured by day.
        """
        schedule = {}
        try:
            # Выполняем запрос с JOIN для связанных таблиц через Django ORM
            schedule_data = GroupSchedule.objects.select_related(
                'group', 'day', 'class_time', 'week_type', 'classroom', 'subject', 'lesson_type', 'teacher'
            ).filter(
                Q(teacher__id=teacher_id) &       # Фильтруем по ID учителя
                ~Q(teacher__first_name="") &      # Учитель должен иметь непустое имя
                ~Q(teacher__last_name="")         # Учитель должен иметь непустую фамилию
            )

            # Отладочный вывод: вывести все данные, извлеченные из базы
            print("Записи для преподавателя с ID:", teacher_id)
            for record in schedule_data:
                print(f"День: {record.day.name}, Неделя: {record.week_type.name}, "
                      f"Время: {record.class_time.start_time} - {record.class_time.end_time}, "
                      f"Аудитория: {record.classroom.building} {record.classroom.room_number}, "
                      f"Предмет: {record.subject.name}, Тип занятия: {record.lesson_type.name}, "
                      f"Группа: {record.group.group_number}")

            # Преобразование результата запроса в структурированный формат
            for record in schedule_data:
                day_name = record.day.name
                week_type = record.week_type.name

                # Данные о каждом занятии
                pair_data = {
                    'Время начала': record.class_time.start_time,
                    'Время конца': record.class_time.end_time,
                    'Корпус': record.classroom.building,
                    'Номер аудитории': record.classroom.room_number,
                    'Наименование предмета': record.subject.name,
                    'Тип занятия': record.lesson_type.name,
                    'Группы': [record.group.group_number]
                }

                # Добавляем занятие в расписание
                if day_name not in schedule:
                    schedule[day_name] = []

                # Агрегируем группы для одного и того же времени занятия
                existing_period = next((item for item in schedule[day_name] if
                                        item['Данные пары']['Время начала'] == pair_data['Время начала'] and
                                        item['Данные пары']['Номер аудитории'] == pair_data['Номер аудитории'] and
                                        item["Неделя"] == week_type), None)
                if existing_period:
                    existing_period['Данные пары']['Группы'].extend(pair_data['Группы'])
                else:
                    schedule[day_name].append({'Неделя': week_type, 'Данные пары': pair_data})

            # Если указан текущий день, фильтруем расписание
            if current_day:
                schedule = {current_day: schedule.get(current_day, [])}

            # Сортируем дни недели по времени начала занятий
            sorted_schedule = {day: sorted(day_schedule, key=lambda x: x['Данные пары']['Время начала']) for
                               day, day_schedule in schedule.items()}

            schedule = sorted_schedule

        except ObjectDoesNotExist:
            print(f"Преподаватель с ID {teacher_id} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при получении расписания для преподавателя с ID {teacher_id}: {str(e)}")
        finally:
            if correlation_id and reply_to:
                result = {'result': schedule}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return schedule
    @staticmethod
    @app.task(name='bot.tasks.get_schedule')
    def get_schedule(group_number: int, current_day: Optional[str] = None, reply_to = None, correlation_id = None):
        schedule = {}
        try:
            group_number = int(group_number)
            GroupSchedule.set_schedule(group_number)
            group_id = Group.objects.get(group_number=group_number)

            # Получение расписания для группы
            group_schedule_data = list(GroupSchedule.objects.select_related(
                    'day',  # Связанная модель для дня недели (Weekday)
                    'class_time',  # Связанная модель для времени занятия (ClassTime)
                    'week_type',  # Связанная модель для типа недели (WeekType)
                    'classroom',  # Связанная модель для аудитории (ClassRoom)
                    'subject',  # Связанная модель для предмета (Subject)
                    'lesson_type',  # Связанная модель для типа занятия (LessonType)
                    'teacher'  # Связанная модель для преподавателя (Teacher)
                ).filter(
                    group_id=group_id  # Фильтрация по group_id
                ).order_by(
                    'day__id',  # Сортировка по дню недели (Weekday)
                    'class_time__id',  # Сортировка по времени занятия (ClassTime)
                    'week_type__id'  # Сортировка по типу недели (WeekType)
                )
            )


            # Структура для хранения расписания группы
            teacher_schedule_cache = {}
            # Сопоставление расписания группы с расписанием преподавателя
            for record in group_schedule_data:
                if record.teacher.id not in teacher_schedule_cache:
                    teacher_schedule_cache[record.teacher.id] = GroupSchedule.get_schedule_teacher(record.teacher.id)

                teacher_schedule = GroupSchedule.get_schedule_teacher(record.teacher.id)  # НУЖНО ОБЯЗАТЕЛЬНО СДЕЛАТЬ ВРЕМЕННОЕ ХРАНЕНИЕ РАСПИСАНИЯ ПРЕПОДАВАТЕЛЯ ЕСЛИ ОНО УЖЕ БЫЛО ПРОСОТРЕНО

                day_name = record.day.name
                week_type = record.week_type.name

                pair_data = {
                    'Время начала': record.class_time.start_time,
                    'Время конца': record.class_time.end_time,
                    'Корпус': record.classroom.building,
                    'Номер аудитории': record.classroom.room_number,
                    'Наименование предмета': record.subject.name,
                    'Тип занятия': record.lesson_type.name,
                    'Фамилия преподавателя': record.teacher.last_name,
                    'Имя преподавателя': record.teacher.first_name,
                    'Отчество преподавателя': record.teacher.middle_name,
                    'Группы': []
                }

                # Проверяем, есть ли у преподавателя другие группы в это время
                for teacher_day, teacher_day_schedule in teacher_schedule.items():
                    if teacher_day == day_name:
                        for teacher_pair in teacher_day_schedule:
                            if teacher_pair['Данные пары']['Время начала'] == pair_data['Время начала'] and \
                                    teacher_pair['Данные пары']['Номер аудитории'] == pair_data['Номер аудитории']:
                                # Исключаем текущую группу из списка
                                other_groups = [grp for grp in teacher_pair['Данные пары']['Группы'] if
                                                grp != group_number]
                                pair_data['Группы'].extend(other_groups)

                if day_name not in schedule:
                    schedule[day_name] = []

                schedule[day_name].append({'Неделя': week_type, 'Данные пары': pair_data})

            if current_day:
                schedule = {current_day: schedule.get(current_day, [])}

        except ObjectDoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
        except Exception as e:
            print(f"Произошла ошибка при получении расписания для группы {group_number}: {str(e)}")

        finally:
            print(reply_to, correlation_id)
            if reply_to is not None and correlation_id is not None:
                result = {'result': schedule}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                print('Отправляю хуй')
                return schedule

    @staticmethod
    @app.task(name='bot.tasks.get_teachers_for_group')
    def get_teachers_for_group(group_number: int, reply_to, correlation_id):
        teacher_list = []
        try:
            group = Group.objects.get(group_number = group_number)
            group_id = group.id
            # Получаем список преподавателей для группы
            teachers = list(
                    Teacher.objects.filter(
                        groupschedule__group_id=group_id  # JOIN с GroupSchedule и фильтрация по group_id
                    ).distinct().values(
                        'id', 'last_name', 'first_name', 'middle_name'  # Выбираем нужные поля
                    )
                )

            # Преобразовываем результат в список словарей
            teacher_list = []
            for teacher in teachers:
                teacher_list.append({
                    'id': teacher['id'],  # Доступ через ключ словаря, а не как атрибут объекта
                    'last_name': teacher['last_name'],
                    'first_name': teacher['first_name'],
                    'middle_name': teacher['middle_name']
                })

        except ObjectDoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
        finally:
            result = {'result': teacher_list}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_pare_for_group')
    def get_pare_for_group(group_id: int, classtime_id: int, weekday_name: str):
        day_id = Weekday.objects.get(name=weekday_name).id
        selected_pare = GroupSchedule.objects.filter(
            group_id=group_id,
            class_time_id=classtime_id,
            day_id=day_id
        )
        group_number = Group.objects.get(id=group_id).group_number
        schedule = {}

        for record in selected_pare:
            teacher_schedule = GroupSchedule.get_schedule_teacher(record.teacher_id)

            day_name = record.day_id.name
            week_type = record.week_type_id.name

            pair_data = {
                'Время начала': record.class_time_id.start_time,
                'Время конца': record.class_time_id.end_time,
                'Корпус': record.classroom_id.building,
                'Номер аудитории': record.classroom_id.room_number,
                'Наименование предмета': record.subject_id.name,
                'Тип занятия': record.lesson_type_id.name,
                'Фамилия преподавателя': record.teacher_id.last_name,
                'Имя преподавателя': record.teacher_id.first_name,
                'Отчество преподавателя': record.teacher_id.middle_name,
                'Группы': []
            }

            for teacher_day, teacher_day_schedule in teacher_schedule.items():
                if teacher_day == day_name:
                    for teacher_pair in teacher_day_schedule:
                        if (teacher_pair['Данные пары']['Время начала'] == pair_data['Время начала'] and
                            teacher_pair['Данные пары']['Номер аудитории'] == pair_data['Номер аудитории']):
                            other_groups = [grp for grp in teacher_pair['Данные пары']['Группы'] if grp != group_number]
                            pair_data['Группы'].extend(other_groups)

            if day_name not in schedule:
                schedule[day_name] = []

            schedule[day_name].append({'Неделя': week_type, 'Данные пары': pair_data})

        final_schedule = {weekday_name: schedule.get(weekday_name, [])}
        return final_schedule

    @staticmethod
    @app.task(name='bot.tasks.filter_groups_by_pare_time')
    def filter_groups_by_pare_time(faculty_id: int, pare_time_id: int) -> Dict[str, int]:
        try:
            query = (
                Group.objects.filter(
                    faculty_id=faculty_id,
                    groupschedule__class_time_id=pare_time_id
                )
                .distinct()
                .values('group_number', 'id')
            )
            filtered_groups = {entry['group_number']: entry['id'] for entry in query}
            return filtered_groups
        except Exception as e:
            print(f"Ошибка при фильтрации групп: {e}")
            return {}
    @staticmethod
    @app.task(name='bot.tasks.get_free_audience')
    def get_free_audience(class_time_id: int, building: str, week_type_id: int, week_day_id: int):
        # Занятые аудитории
        list_busy_audience = Classroom.objects.filter(
            groupschedule__class_time_id=class_time_id,
            groupschedule__week_type_id=week_type_id,
            building=building,
            groupschedule__day_id=week_day_id
        ).values('building', 'room_number')

        # Все аудитории
        list_all_audience = Classroom.objects.filter(
            building=building,
            groupschedule__week_type_id=week_type_id,
            groupschedule__day_id=week_day_id
        ).values('building', 'room_number')

        # Преобразуем в множества
        all_set = {(aud['building'], aud['room_number']) for aud in list_all_audience}
        busy_set = {(aud['building'], aud['room_number']) for aud in list_busy_audience}

        # Находим свободные аудитории
        free_set = all_set - busy_set

        free_audience_dict = {}
        for building, room_number in free_set:
            if building not in free_audience_dict:
                free_audience_dict[building] = []
            free_audience_dict[building].append(room_number)

        return free_audience_dict            
