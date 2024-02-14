from peewee import CharField, IntegrityError, DoesNotExist

from ORM.database_declaration_and_exceptions import BaseModel


class Teacher(BaseModel):
    """
    A class to manage teacher records in an educational institution.

    Attributes:
        last_name (CharField): The last name of the teacher.
        first_name (CharField): The first name of the teacher.
        middle_name (CharField): The middle name of the teacher.
    """

    last_name = CharField()
    first_name = CharField()
    middle_name = CharField()

    @staticmethod
    def add_teacher(last_name, first_name, middle_name):
        """
        Adds a new teacher to the database.

        Params:
            last_name (str): The last name of the teacher.
            first_name (str): The first name of the teacher.
            middle_name (str): The middle name of the teacher.
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
        Returns the ID of a teacher by their full name.

        Params:
            last_name (str), first_name (str), middle_name (str): Full name of the teacher.

        Returns:
            int: The ID of the teacher.
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


class Subject(BaseModel):
    """
    A class to manage subjects in an educational institution.

    Attributes:
        name (CharField): Unique name of the subject.
    """

    name = CharField(unique=True)

    @staticmethod
    def add_subject(name):
        """
        Adds a new subject to the database.

        Params:
            name (str): The name of the subject to add.
        """
        try:
            subject = Subject.create(name=name)
            print(f"Subject '{name}' successfully added.")
            return subject.id
        except IntegrityError:
            print(f"Subject '{name}' already exists in the database.")

    @staticmethod
    def get_subject_id(subject_name):
        """
        Returns the ID of a subject by its name.

        Params:
            subject_name (str): The name of the subject.

        Returns:
            int: The ID of the subject.
        """
        try:
            subject = Subject.get(Subject.name == subject_name)
            return subject.id
        except Exception as e:
            raise ValueError(f"Subject named {subject_name} not found: {str(e)}")


class LessonType(BaseModel):
    """
    A class to manage lesson types within an educational institution.

    Attributes:
        name (CharField): Unique name of the lesson type.
    """

    name = CharField(unique=True)

    @staticmethod
    def initialize_lesson_type():
        """
        Initializes the database with predefined lesson types.
        """
        lesson_types = ['Лекция', 'Практическое занятие', 'Лабораторное занятие']

        for lesson_type in lesson_types:
            try:
                LessonType.create(name=lesson_type)
                print(f"Lesson type '{lesson_type}' successfully added.")
            except IntegrityError:
                print(f"Lesson type '{lesson_type}' already exists in the database.")

    @staticmethod
    def get_lesson_type_id(lesson_type_name):
        """
        Returns the ID of a lesson type by its name.

        Params:
            lesson_type_name (str): The name of the lesson type.

        Returns:
            int: The ID of the lesson type.
        """
        try:
            lesson_type = LessonType.get(LessonType.name == lesson_type_name)
            return lesson_type.id
        except DoesNotExist:
            raise ValueError(f"Lesson type '{lesson_type_name}' not found")


class Classroom(BaseModel):
    """
    A class to manage classroom records in an educational institution.

    Attributes:
        building (CharField): The building where the classroom is located.
        room_number (CharField): The room number of the classroom.
    """

    building = CharField()
    room_number = CharField()

    @staticmethod
    def add_classroom(building, room_number):
        """
        Adds a new classroom to the database.

        Params:
            building (str): The building of the new classroom.
            room_number (str): The room number of the new classroom.
        """
        try:
            classroom = Classroom.create(building=building, room_number=room_number)
            print(f"Classroom '{building}{room_number}' successfully added.")
            return classroom.id
        except IntegrityError:
            print(f"Classroom '{building}{room_number}' already exists in the database.")

    @staticmethod
    def get_classroom_id(building, room_number):
        """
        Returns the ID of a classroom by its location and room number.

        Params:
            building (str), room_number (str): The location of the classroom.

        Returns:
            int: The ID of the classroom.
        """
        try:
            classroom = Classroom.get(
                Classroom.building == building,
                Classroom.room_number == room_number
            )
            return classroom.id
        except DoesNotExist:
            raise ValueError(f"Classroom in building {building}, room number {room_number} not found")