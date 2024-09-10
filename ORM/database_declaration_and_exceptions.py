from peewee import PostgresqlDatabase, Model, SqliteDatabase, MySQLDatabase
import pytz

from Path.path_base import path_base

# Установка часового пояса для Москвы (+3 часа относительно Лондона)
moscow_tz = pytz.timezone('Europe/Moscow')

# db = PostgresqlDatabase('postgres', user='postgres', password='0000', host='localhost', port=5432)
# db = SqliteDatabase(path_base.db_path)
db = MySQLDatabase(
    'schedule',
    user='schedule_SMTU',
    password='wD7jQ#2zRt!vY6Tp',
    host='localhost',
    port=3306
)

class DataBaseException(BaseException):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class BaseModel(Model):
    class Meta:
        database = db
