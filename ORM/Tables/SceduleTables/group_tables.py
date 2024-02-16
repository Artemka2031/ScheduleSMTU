from peewee import CharField, IntegrityError, DoesNotExist, IntegerField, ForeignKeyField

from ORM.database_declaration_and_exceptions import BaseModel
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
