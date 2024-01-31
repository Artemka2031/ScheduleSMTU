from peewee import PostgresqlDatabase, Model, SqliteDatabase

# db = PostgresqlDatabase('postgres', user='postgres', password='0000', host='localhost', port=5432)
db = SqliteDatabase("database.db")

class DataBaseException(BaseException):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class BaseModel(Model):
    class Meta:
        database = db
