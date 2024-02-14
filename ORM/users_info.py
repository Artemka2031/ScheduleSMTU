from datetime import datetime

from peewee import ForeignKeyField, IntegerField, IntegrityError, DoesNotExist, TextField, DateTimeField, fn, DateField

from ORM.schedule_information import Group
from ORM.database_declaration_and_exceptions import BaseModel, moscow_tz


class User(BaseModel):
    user_id = IntegerField(unique=True)
    group_number = IntegerField(unique=False)
    group_id = ForeignKeyField(Group, backref='users')

    @staticmethod
    def get_user(user_id: int):
        try:
            return User.get(User.user_id == user_id)
        except DoesNotExist:
            return None

    @staticmethod
    def get_group_number(user_id: int):
        try:
            user = User.get(User.user_id == user_id)
            return user.group_number
        except DoesNotExist:
            raise ValueError(f"Пользователь с идентификатором '{user_id}' не найден")

    @staticmethod
    def registrate_user(user_id, group_number):
        try:
            # Проверяем, существует ли группа
            group = Group.get(Group.group_number == group_number)

            # Создаем запись о пользователе
            user = User.create(user_id=user_id, group_number=group_number, group_id=group)
            print(f"Пользователь '{user_id}' успешно зарегистрирован в группе '{group_number}'.")
        except DoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
        except IntegrityError:
            print(f"Пользователь с идентификатором '{user_id}' уже существует в базе данных.")

    @staticmethod
    def change_group_number(user_id, new_group_number):
        try:
            # Проверяем, существует ли новая группа
            new_group = Group.get(Group.group_number == new_group_number)

            # Находим пользователя по ID
            user = User.get(User.user_id == user_id)

            # Обновляем номер группы и внешний ключ
            user.group_number = new_group_number
            user.group_id = new_group
            user.save()

            print(f"Номер группы пользователя '{user_id}' успешно изменен на '{new_group_number}'.")
        except DoesNotExist:
            print(f"Группа с номером {new_group_number} не найдена.")
            print(f"Или пользователь с идентификатором '{user_id}' не найден.")


    @staticmethod
    def get_all_users():
        user_ids = [user.user_id for user in User.select(User.user_id)]
        return user_ids


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

if __name__=="__main__":
    print(User.get_all_users())