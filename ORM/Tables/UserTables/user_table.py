from datetime import datetime

from peewee import ForeignKeyField, IntegerField, IntegrityError, DoesNotExist, TextField, DateTimeField, fn, DateField

from ORM.Tables.SceduleTables.group_tables import Group
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
    def get_all_users_ids():
        user_ids = [user.user_id for user in User.select(User.user_id)]
        return user_ids

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
