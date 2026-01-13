import asyncio
import json
import logging

from aiogram.utils.markdown import hbold
from asgiref.sync import async_to_sync
from celery import shared_task
from celery.bin.result import result
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.rabbitmq_consumer import logger
from djcore.apps.database.utils.Path.path_base import path_base
from djcore.apps.database.utils.Path.schedule_path_functions import get_faculties_and_groups
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app

class Faculty(models.Model):
    name = models.CharField(unique=True, max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'faculty'

    @staticmethod
    def add_faculty(name):
        """
        Adds a new faculty to the database.

        Params:
            name (str): The name of the faculty to add.

        """
        try:
            Faculty.objects.create(name=name)
            print(f"Faculty '{name}' successfully added.")
        except IntegrityError:
            print(f"Faculty '{name}' already exists in the database.")

    @staticmethod
    def get_faculty_id(faculty_name, reply_to = None, correlation_id = None):
        """
        Returns the ID of a faculty by its name.

        Params:
            faculty_name (str): The name of the faculty.

        Returns:
            int: The ID of the faculty.
        """
        faculty = None
        try:
            faculty = Faculty.objects.get(name = faculty_name)
            #return faculty.id
        except ObjectDoesNotExist:
            raise ValueError(f"Faculty '{faculty_name}' not found")
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': faculty.id}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return faculty.id

    @staticmethod
    @app.task(name='bot.tasks.get_all_faculties')
    def get_all_faculties(reply_to=None, correlation_id=None):
        return_faculties = {}
        try:
            # Получаем все факультеты
            faculties = Faculty.objects.all()  # Аналог `Faculty.select()` в Peewee

            # Преобразуем в словарь {название: ID}
            return_faculties = {faculty.name: faculty.id for faculty in faculties}

            print(f"Получено {len(return_faculties)} факультетов.")

        except Exception as e:
            print(f"Ошибка при получении списка факультетов: {e}")

        finally:
            # Отправляем результат через RabbitMQ
            asyncio.run(send_response({'result': return_faculties}, reply_to, correlation_id))

    @staticmethod
    @app.task(name='admin_bot.tasks.get_faculty_name_by_id')
    def get_faculty_name_by_id(faculty_id, reply_to=None, correlation_id=None):
        faculty_name = None
        try:
            faculty_name = Faculty.objects.get(id=faculty_id).name
        except ObjectDoesNotExist:
            print(f'Faculty {faculty_id} does not exist')
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': faculty_name}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return faculty_name

    @staticmethod
    def add_faculties_and_groups():
        """
        Adds Schedule and their associated groups to the database based on predefined data.
        """
        faculties_and_groups = get_faculties_and_groups()

        for faculty_name, group_numbers in faculties_and_groups.items():
            Faculty.add_faculty(faculty_name)  # Adding faculty

            for group_number in group_numbers:
                Group.add_group(group_number, faculty_name)  # Adding group to the faculty

class Department(models.Model):
    name = models.CharField(unique=True, max_length=255)
    faculty = models.ForeignKey('Faculty', models.DO_NOTHING)
    objects = models.Manager()
    class Meta:
        db_table = 'department'

    @staticmethod
    def add_department(department_name, faculty_name):
        """
        Creates a new department and links it to an existing faculty.

        Params:
            department_name (str): The name of the department to add.
            faculty_name (str): The name of the faculty to link with.

        """
        try:
            faculty = Faculty.objects.get(name = faculty_name)
            Department.objects.create(name=department_name, faculty=faculty)
            print(f"Department '{department_name}' successfully added to Faculty '{faculty_name}'.")
        except ObjectDoesNotExist:
            print(f"Faculty '{faculty_name}' not found.")
        except IntegrityError:
            print(f"Department '{department_name}' already exists.")

    @staticmethod
    def get_department_id(department_name):
        """
        Returns the ID of a department by its name.

        Params:
            department_name (str): The name of the department.

        Returns:
            int: The ID of the department.
        """
        try:
            department = Department.objects.get(name = department_name)
            return department.id
        except ObjectDoesNotExist:
            raise ValueError(f"Department '{department_name}' not found")

class Teacher(models.Model):
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'teacher'

    @staticmethod
    def add_teacher(last_name, first_name, middle_name):
        """
        Adds a new teacher_text to the database.

        Params:
            last_name (str): The last name of the teacher_text.
            first_name (str): The first name of the teacher_text.
            middle_name (str): The middle name of the teacher_text.
        """
        try:
            teacher = Teacher.objects.create(last_name=last_name, first_name=first_name, middle_name=middle_name)
            print(f"Teacher {last_name} {first_name} {middle_name} successfully added.")
            return teacher.id
        except IntegrityError:
            print(f"Teacher {last_name} {first_name} {middle_name} already exists in the database.")

    @staticmethod
    def get_teacher_id(last_name, first_name, middle_name):
        """
        Retrieves the ID of a teacher_text based on their full name.

        Params:
            last_name (str): The last name of the teacher_text.
            first_name (str): The first name of the teacher_text.
            middle_name (str): The middle name of the teacher_text.

        Returns:
            int: The ID of the teacher_text if found, otherwise raises ValueError.
        """
        try:
            teacher = Teacher.objects.get(
                last_name = last_name,
                first_name = first_name,
                middle_name = middle_name
            )
            return teacher.id
        except ObjectDoesNotExist:
            raise ValueError(f"Teacher {last_name} {first_name} {middle_name} not found")

    @staticmethod
    @app.task(name='bot.tasks.get_teacher_by_last_name')
    def get_teacher_by_last_name(last_name, reply_to, correlation_id):
        # Используем запрос LIKE для поиска всех преподавателей, чьи фамилии соответствуют или содержат заданную строку
        teachers = Teacher.objects.filter(last_name__icontains=last_name).all()
        # teachers = Teacher.select().where(Teacher.last_name.contains(last_name))

        if not teachers:
            # Если преподаватели с такой фамилией не найдены, выбрасываем исключение
            raise ValueError(f"Преподаватель с фамилией {hbold(last_name)} не найден.")
        result = {'result': [{'id': teacher.id, 'last_name': teacher.last_name, 'first_name': teacher.first_name,
                 'middle_name': teacher.middle_name} for teacher in teachers]}
        asyncio.run(send_response(result, reply_to, correlation_id))



    @staticmethod
    @app.task(name='bot.tasks.get_teacher')
    def get_teacher(teacher_id, reply_to, correlation_id):
        find_teacher = {}
        try:
            teacher = Teacher.objects.get(id = teacher_id)
            find_teacher = {
                'last_name': teacher.last_name,
                'first_name': teacher.first_name,
                'middle_name': teacher.middle_name
            }

        except ObjectDoesNotExist:
            print(f"Преподаватель с ID {teacher_id} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при получении данных о преподавателе: {str(e)}")
        finally:
            result = {'result': find_teacher}
            asyncio.run(send_response(result, reply_to, correlation_id))

class TeacherDepartment(models.Model):
    teacher = models.OneToOneField(Teacher, models.DO_NOTHING, primary_key=True)  # The composite primary key (teacher_id, department_id) found, that is not supported. The first column is selected.
    department = models.ForeignKey(Department, models.DO_NOTHING)
    objects = models.Manager()
    class Meta:
        db_table = 'teacherdepartment'
        unique_together = (('teacher', 'department'), ('teacher', 'department'),)

    @staticmethod
    def get_teacher_department_id(teacher_id, department_id):
        """
        Retrieves the ID of a teacher_text department association based on their IDs.

        Params:
            teacher_id (int): The ID of the teacher_text.
            department_id (int): The ID of the department.

        Returns:
            int: The ID of the teacher_text department association if found, otherwise raises ValueError.
        """
        try:
            teacher_department = TeacherDepartment.objects.get(
                teacher = teacher_id,
                department = department_id
            )
            return teacher_department.id
        except ObjectDoesNotExist:
            raise ValueError(f"Teacher department association between {teacher_id} and {department_id} not found")

    @staticmethod
    @app.task(name='admin_bot.tasks.get_teachers_for_faculty')
    def get_teachers_for_faculty(department_id, reply_to, correlation_id):
        teacher_list = []
        try:
            teachers = list(
                Teacher.objects.filter(teacherdepartment__department__faculty__id=department_id).distinct().values(
                    'id', 'last_name', 'first_name', 'middle_name'
                )
            )
            for teacher in teachers:
                teacher_list.append({
                    'id': teacher['id'],  # Доступ через ключ словаря, а не как атрибут объекта
                    'last_name': teacher['last_name'],
                    'first_name': teacher['first_name'],
                    'middle_name': teacher['middle_name']
                })

        except ObjectDoesNotExist:
            logger(f"Факультет с id {department_id} не найден.")

        except Exception as e:
            logger(f"Произошла ошибка: {str(e)}")
        finally:
            result = {'result': teacher_list}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    def set_teachers_department():
        """
        Sets the department for each teacher in the database based on the department data file.
        If a department is not found, it will be added.
        """
        with open(path_base.department_data, 'r', encoding='utf-8') as file:
            department_data = json.load(file)
        for faculty_data in department_data:
            faculty_name = faculty_data['faculty']
            for department_info in faculty_data['departments']:
                print(department_info)
                department_name = department_info['name']
                # Проверка существования факультета, если отсутствует, добавляем
                faculty, created = Faculty.objects.get_or_create(name=faculty_name)
                if created:
                    print(f"Faculty '{faculty_name}' added.")

                # Проверка существования кафедры, если отсутствует, добавляем
                department, created = Department.objects.get_or_create(name=department_name, faculty=faculty)
                if created:
                    print(f"Department '{department_name}' added to Faculty '{faculty_name}'.")

                for employee in department_info['Employees']:
                    try:
                        teacher = Teacher.objects.get(
                            last_name=employee['surname'],
                            first_name=employee['name'],
                            middle_name=employee['patronymic']
                        )
                        try:
                            TeacherDepartment.objects.get_or_create(teacher=teacher, department=department)
                        except IntegrityError:
                            # Если возникла ошибка дублирования, пытаемся получить уже существующую запись
                            TeacherDepartment.objects.get(teacher=teacher, department=department)
                    except ObjectDoesNotExist:
                        print(f"Teacher {employee['surname']} {employee['name']} not found.")

class Group(models.Model):
    group_number = models.IntegerField(unique=True)
    faculty = models.ForeignKey(Faculty, models.DO_NOTHING)
    objects = models.Manager()
    class Meta:
        db_table = 'group'
    @staticmethod
    def add_group(group_number: int, faculty_name):
        """
        Adds a new group to a specified faculty.

        Params:
            group_number (int): The number of the group to add.
            faculty_name (str): The name of the faculty to which the group belongs.
        """
        try:
            faculty = Faculty.objects.get(name = faculty_name)
            Group.objects.create(group_number=group_number, faculty=faculty)
            print(f"Group '{group_number}' successfully added to faculty '{faculty_name}'.")
        except IntegrityError:
            print(f"Group '{group_number}' already exists in the database or faculty '{faculty_name}' not found.")

    @staticmethod
    @app.task(name='bot.tasks.get_group_id')
    def get_group_id(group_number, reply_to=None, correlation_id=None):
        logger.info(
            f"Задача get_group_id запущена с параметрами: group_number={group_number}, reply_to={reply_to}, correlation_id={correlation_id}")

        group_id = None
        try:
            logger.info(f"Пытаемся найти группу с номером: {group_number}")
            group = Group.objects.get(group_number=group_number)
            group_id = group.id
            logger.info(f"Группа найдена: {group_id}")
        except ObjectDoesNotExist:
            group_id = None
            logger.error(f"Группа с номером {group_number} не найдена")
            raise ValueError(f"Group number {group_number} not found")
        finally:
            if reply_to and correlation_id:
                result = {'result': group_id}
                logger.info(f"Отправляем результат: {result}")
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return group_id

    @staticmethod
    @app.task(name='admin_bot.tasks.get_group_number')
    def get_group_number(group_id, reply_to=None, correlation_id=None):
        group_number = None
        try:
            group_number = Group.objects.get(id=group_id).group_number
        except Group.DoesNotExist:
            raise ValueError(f"Group number {group_id} not found")
        finally:
            if reply_to and correlation_id:
                result = {'result': group_number}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return group_number


'''
Убрать метод ниже, в group_schedule уже прописан метод, его заменяющий
'''
    # @staticmethod
    # @app.task(name='bot.tasks.get_all_group_for_faculty')
    # def get_all_group_for_faculty(faculty_id) -> dict:
    #     group_list = {}
    #     try:
    #         groups = Group.objects.filter(faculty=faculty_id)
    #
    #         for group in groups:
    #             group_list[group.group_number] = group.id
    #
    #         return group_list
    #     except Group.DoesNotExist:
    #         raise ValueError(f"Faculty number {faculty_id} not found")
