import json
from Paths
from peewee import SqliteDatabase, Model, CharField, IntegrityError
from prettytable import PrettyTable

# Определение модели
db = SqliteDatabase('example.db')


class BaseModel(Model):
    class Meta:
        database = db


class MyModel(BaseModel):
    faculty = CharField()
    group = CharField()
    day_of_week = CharField()
    time = CharField()
    week = CharField()
    location_building = CharField()
    location_room = CharField()
    subject_name = CharField()
    lesson_type = CharField()
    additional_info = CharField()
    instructor_last_name = CharField()
    instructor_first_name = CharField()
    instructor_middle_name = CharField()

    @classmethod
    def add_group_from_json(cls, ):
        json_path = Paths.schedule_smtu_dir
        with open(json_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        for faculty, groups_data in json_data.items():
            for group, schedule_data in groups_data.items():
                for entry in schedule_data.get("schedule", []):
                    try:
                        location_info = entry.get('Аудитория', {})
                        subject_info = entry.get('Предмет', {})
                        instructor_info = entry.get('Преподаватель', {})

                        time_value = entry.get("Время")
                        if time_value is None:
                            continue

                        cls.create(
                            faculty=faculty,
                            group=group,
                            day_of_week=entry.get("День недели"),
                            time=time_value,
                            week=entry.get("Неделя"),
                            location_building=location_info.get('Корпус'),
                            location_room=location_info.get('Номер аудитории'),
                            subject_name=subject_info.get('Наименование предмета'),
                            lesson_type=subject_info.get('Тип занятия'),
                            additional_info=subject_info.get('Дополнительная информация'),
                            instructor_last_name=instructor_info.get('Фамилия'),
                            instructor_first_name=instructor_info.get('Имя'),
                            instructor_middle_name=instructor_info.get('Отчество')
                        )
                    except IntegrityError as e:
                        # Обработка ошибки IntegrityError (например, если запись уже существует)
                        print(f"Ошибка IntegrityError: {e}")


# Пример использования
MyModel.add_group_from_json()




