import json
from pathlib import Path

from peewee import *
from Parsing.Paths import db, schedule_smtu_min_json



# Определение модели
db = SqliteDatabase(db)


class BaseMode(Model):
    class Meta:
        database = db


class MyModel(BaseMode):
    key = CharField()
    value = CharField()


# Создание таблицы
# db.connect()
# db.create_tables([MyModel])


json_file_path = Path('Schedule_smtu') / "Schedule_smtu.json"

# Открытие и чтение данных из JSON-файла
with open(json_file_path, 'r') as file:
    json_data = json.load(file)
print(json_data)
# def create_tables():
