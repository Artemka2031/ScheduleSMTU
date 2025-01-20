from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from djcore.celery_app import app


class Subject(models.Model):
    name = models.CharField(unique=True, max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'subject'
        managed = True
    @staticmethod
    def add_subject(name):
        """
        Adds a new subject to the database.

        Params:
            name (str): The name of the subject to add.
        """
        try:
            subject = Subject.objects.create(name=name)
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
            subject = Subject.objects.get(name = subject_name)
            return subject.id
        except Exception as e:
            raise ValueError(f"Subject named {subject_name} not found: {str(e)}")

class LessonType(models.Model):
    name = models.CharField(unique=True, max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'lessontype'
        managed = True
    @staticmethod
    def initialize_lesson_type():
        """
        Initializes the database with predefined lesson types.
        """
        lesson_types = ['Лекция', 'Практическое занятие', 'Лабораторное занятие']

        for lesson_type in lesson_types:
            try:
                LessonType.objects.create(name=lesson_type)
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
            lesson_type = LessonType.objects.get(name = lesson_type_name)
            return lesson_type.id
        except ObjectDoesNotExist:
            raise ValueError(f"Lesson type '{lesson_type_name}' not found")

class ClassRoom(models.Model):
    building = models.CharField(max_length=255)
    room_number = models.CharField(max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'classroom'
        managed = True

    @staticmethod
    def add_classroom(building, room_number):
        """
        Adds a new classroom to the database.

        Params:
            building (str): The building of the new classroom.
            room_number (str): The room number of the new classroom.
        """
        try:
            classroom = ClassRoom.objects.create(building=building, room_number=room_number)
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
            classroom = ClassRoom.objects.get(
                building = building,
                room_number = room_number
            )
            return classroom.id
        except ObjectDoesNotExist:
            raise ValueError(f"Classroom in building {building}, room number {room_number} not found")