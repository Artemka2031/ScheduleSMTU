from datetime import datetime
from typing import Dict

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

    @staticmethod
    def get_user_suggestion() -> Dict[int, str]:
        user_suggestions = {}
        try:
            # Get all users who sent suggestions
            users = User.select().join(Suggestion).distinct()

            for user in users:
                # Get the latest suggestion for each user
                latest_suggestion = Suggestion.select().where(Suggestion.user_id == user.id).order_by(
                    Suggestion.date.desc()).get()
                user_suggestions[user.user_id] = latest_suggestion.suggestion  # Change id to user_id

            return user_suggestions
        except DoesNotExist:
            print("No suggestions found.")
            return 0

    @staticmethod
    def delete_suggestion(user_id: int, suggestion: str):
        try:
            user = User.get(User.user_id == user_id)
            Suggestion.get((Suggestion.user_id == user) & (Suggestion.suggestion == suggestion)).delete_instance()
            print("Предложение успешно удалено.")
        except DoesNotExist:
            print(f"Предложение от пользователя с user_id {user_id} и текстом {suggestion} не найдено.")