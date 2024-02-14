from datetime import datetime

from peewee import ForeignKeyField, IntegrityError, DoesNotExist, TextField, DateField

from ORM.Tables.UserTables.user_table import User
from ORM.database_declaration_and_exceptions import BaseModel, moscow_tz


class Suggestion(BaseModel):
    user_id = ForeignKeyField(User, backref='suggestions')
    suggestion = TextField()
    date = DateField()

    @staticmethod
    def add_suggestion(user_id: int, suggestion: str):
        try:
            user = User.get(User.user_id == user_id)

            # Создаем запись в таблице Suggestion
            Suggestion.create(user_id=user, suggestion=suggestion, date=datetime.now(moscow_tz).date().day)
            print("Предложение успешно добавлено.")
        except DoesNotExist:
            print(f"Пользователь с user_id {user_id} не найден.")
        except IntegrityError:
            print(f"Предложение от пользователя {user_id} уже существует в базе данных.")

    @staticmethod
    def get_user_suggestions_count(user_id: int) -> int:
        try:
            # Получаем текущую дату
            current_date = datetime.now(moscow_tz).date().day

            # Используем count для подсчета строк по заданным условиям
            count = Suggestion.select().where(
                (Suggestion.user_id == User.get_user(user_id)) &  # Фильтр по пользователю
                (Suggestion.date == current_date)  # Фильтр по текущей дате
            ).count()

            return count
        except DoesNotExist:
            print(f"Пользователь с user_id {user_id} не найден.")
            return 0
