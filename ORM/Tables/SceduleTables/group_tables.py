import json
from typing import Dict, List

from aiogram.utils.markdown import hbold
from peewee import CharField, IntegrityError, DoesNotExist, IntegerField, ForeignKeyField, CompositeKey

from ORM.database_declaration_and_exceptions import BaseModel
from Path.path_base import path_base
from Path.schedule_path_functions import get_faculties_and_groups


class Faculty(BaseModel):
    """
    A class to manage Schedule within an educational institution.

    Attributes:
        name (CharField): Unique name of the faculty.
    """

    name = CharField(unique=True)

    @staticmethod
    def add_faculty(name):
        """
        Adds a new faculty to the database.

        Params:
            name (str): The name of the faculty to add.

        """
        try:
            Faculty.create(name=name)
            print(f"Faculty '{name}' successfully added.")
        except IntegrityError:
            print(f"Faculty '{name}' already exists in the database.")

    @staticmethod
    def get_faculty_id(faculty_name):
        """
        Returns the ID of a faculty by its name.

        Params:
            faculty_name (str): The name of the faculty.

        Returns:
            int: The ID of the faculty.
        """
        try:
            faculty = Faculty.get(Faculty.name == faculty_name)
            return faculty.id
        except DoesNotExist:
            raise ValueError(f"Faculty '{faculty_name}' not found")

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


class Department(BaseModel):
    name = CharField(unique=True)
    faculty = ForeignKeyField(Faculty, backref='departments')

    @staticmethod
    def add_department(department_name, faculty_name):
        """
        Creates a new department and links it to an existing faculty.

        Params:
            department_name (str): The name of the department to add.
            faculty_name (str): The name of the faculty to link with.

        """
        try:
            faculty = Faculty.get(Faculty.name == faculty_name)
            Department.create(name=department_name, faculty=faculty)
            print(f"Department '{department_name}' successfully added to Faculty '{faculty_name}'.")
        except DoesNotExist:
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
            department = Department.get(Department.name == department_name)
            return department.id
        except DoesNotExist:
            raise ValueError(f"Department '{department_name}' not found")


class Teacher(BaseModel):
    """
    Represents a teacher_text in an educational institution.
    """
    last_name = CharField()
    first_name = CharField()
    middle_name = CharField()

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
            teacher = Teacher.create(last_name=last_name, first_name=first_name, middle_name=middle_name)
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
            teacher = Teacher.get(
                Teacher.last_name == last_name,
                Teacher.first_name == first_name,
                Teacher.middle_name == middle_name
            )
            return teacher.id
        except DoesNotExist:
            raise ValueError(f"Teacher {last_name} {first_name} {middle_name} not found")

    @staticmethod
    def get_teacher_by_last_name(last_name) -> List[Dict]:
        # Используем запрос LIKE для поиска всех преподавателей, чьи фамилии соответствуют или содержат заданную строку
        teachers = Teacher.select().where(Teacher.last_name.contains(last_name))

        if not teachers:
            # Если преподаватели с такой фамилией не найдены, выбрасываем исключение
            raise ValueError(f"Преподаватель с фамилией {hbold(last_name)} не найден.")

        # Если преподаватели найдены, возвращаем список словарей с их данными
        return [{'id': teacher.id, 'last_name': teacher.last_name, 'first_name': teacher.first_name,
                 'middle_name': teacher.middle_name} for teacher in teachers]

    @staticmethod
    def get_teacher(teacher_id) -> Dict:
        try:
            teacher = Teacher.get(Teacher.id == teacher_id)
            return {
                'last_name': teacher.last_name,
                'first_name': teacher.first_name,
                'middle_name': teacher.middle_name
            }
        except DoesNotExist:
            print(f"Преподаватель с ID {teacher_id} не найден.")
            return {}
        except Exception as e:
            print(f"Произошла ошибка при получении данных о преподавателе: {str(e)}")
            return {}


class TeacherDepartment(BaseModel):
    """
    Represents the association between a teacher_text and a department.
    """
    teacher = ForeignKeyField(Teacher, backref='department_associations')
    department = ForeignKeyField(Department, backref='teacher_associations')

    class Meta:
        primary_key = CompositeKey('teacher_text', 'department')
        indexes = (
            (('teacher_text', 'department'), True),
        )

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
            teacher_department = TeacherDepartment.get(
                TeacherDepartment.teacher == teacher_id,
                TeacherDepartment.department == department_id
            )
            return teacher_department.id
        except DoesNotExist:
            raise ValueError(f"Teacher department association between {teacher_id} and {department_id} not found")

    @staticmethod
    def set_teachers_department():
        """
        Sets the department for each teacher_text in the database based on the department data file.
        If a department is not found, it will be added.
        """
        with open(path_base.department_data, 'r', encoding='utf-8') as file:
            department_data = json.load(file)

        for faculty_data in department_data:
            faculty_name = faculty_data['faculty']
            for department_info in faculty_data['departments']:
                department_name = department_info['name']
                # Проверка существования факультета, если отсутствует, добавляем
                faculty, created = Faculty.get_or_create(name=faculty_name)
                if created:
                    print(f"Faculty '{faculty_name}' added.")

                # Проверка существования кафедры, если отсутствует, добавляем
                department, created = Department.get_or_create(name=department_name, faculty=faculty)
                if created:
                    print(f"Department '{department_name}' added to Faculty '{faculty_name}'.")

                for employee in department_info['Employees']:
                    try:
                        teacher = Teacher.get(
                            Teacher.last_name == employee['surname'],
                            Teacher.first_name == employee['name'],
                            Teacher.middle_name == employee['patronymic']
                        )
                        TeacherDepartment.get_or_create(teacher=teacher, department=department)
                    except DoesNotExist:
                        print(f"Teacher {employee['surname']} {employee['name']} not found.")


class Group(BaseModel):
    """
    A class to manage student groups within Schedule.

    Attributes:
        group_number (IntegerField): Unique number of the group.
        faculty (ForeignKeyField): Reference to the associated faculty.
    """

    group_number = IntegerField(unique=True)
    faculty = ForeignKeyField(Faculty, backref='groups')

    @staticmethod
    def add_group(group_number: int, faculty_name):
        """
        Adds a new group to a specified faculty.

        Params:
            group_number (int): The number of the group to add.
            faculty_name (str): The name of the faculty to which the group belongs.
        """
        try:
            faculty = Faculty.get(Faculty.name == faculty_name)
            Group.create(group_number=group_number, faculty=faculty)
            print(f"Group '{group_number}' successfully added to faculty '{faculty_name}'.")
        except IntegrityError:
            print(f"Group '{group_number}' already exists in the database or faculty '{faculty_name}' not found.")

    @staticmethod
    def get_group_id(group_number) -> int:
        """
        Returns the ID of a group by its number.

        Params:
            group_number (int): The number of the group.

        Returns:
            int: The ID of the group.
        """
        try:
            group = Group.get(Group.group_number == group_number)
            return group.id
        except DoesNotExist:
            raise ValueError(f"Group number {group_number} not found")
