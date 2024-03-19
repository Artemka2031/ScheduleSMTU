from datetime import datetime
from typing import Dict, Any

from peewee import ForeignKeyField, IntegrityError, DoesNotExist, TextField, DateField, DateTimeField, fn, CharField

from ORM.Tables.UserTables.user_table import User
from ORM.database_declaration_and_exceptions import BaseModel, moscow_tz


class Suggestion(BaseModel):
    user_id = ForeignKeyField(User, backref='suggestions', unique=False)
    suggestion = TextField()
    date = DateField()
    closed_date = DateField(default="", null=False)
    closed_text = DateField(default="", null=False)

    @staticmethod
    def add_suggestion(user_id: int, suggestion: str):
        try:
            user = User.get(User.user_id == user_id)
            # Создаем запись в таблице Suggestion
            Suggestion.create(user_id=user, suggestion=suggestion, date=datetime.now(moscow_tz).date())
            print("Предложение успешно добавлено.")
        # except DoesNotExist:
        #     print(f"Пользователь с user_id {user_id} не найден.")
        # except IntegrityError:
        #     print(f"Предложение от пользователя {user_id} уже существует в базе данных.")
        except Exception as e:
            print(f"Произошла ошибка при добавлении предложения: {e}")

    @staticmethod
    def get_user_suggestions_count(user_id: int) -> int:
        try:
            # Получаем текущую дату
            current_date = datetime.now(moscow_tz).date()

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
    def get_user_suggestion() -> Dict[Any, dict]:
        user_suggestions = {}
        try:
            suggestions = Suggestion.select().where(Suggestion.closed_text == '')

            for suggestion in suggestions:
                user_id = suggestion.user_id.user_id
                suggestion_id = suggestion.id
                if user_id not in user_suggestions:
                    user_suggestions[user_id] = {}  # Создаем вложенный словарь для каждого user_id
                user_suggestions[user_id][suggestion_id] = suggestion.suggestion

            return user_suggestions
        except DoesNotExist:
            print("Не найдено предложений.")
            return {}

    @staticmethod
    def process_admin_response(user_id: int, suggestion_id: int, admin_response_date: date,
                               admin_response_text: str):
        try:
            user = User.get(User.user_id == user_id)
            suggestion_instance = Suggestion.get((Suggestion.user_id == user) & (Suggestion.id == suggestion_id))
            suggestion_instance.closed_date = admin_response_date
            suggestion_instance.closed_text = admin_response_text
            suggestion_instance.save()
            print("Дата и ответ администратора успешно заполнены.")
        except DoesNotExist:
            print(f"Предложение от пользователя с user_id {user_id} и текстом {suggestion_id} не найдено.")
