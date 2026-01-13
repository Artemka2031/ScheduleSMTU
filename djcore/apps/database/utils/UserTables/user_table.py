import asyncio
import logging

from asgiref.sync import sync_to_async
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.utils.ScheduleTables.group_tables import Group, Faculty
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class User(models.Model):
    user_id = models.IntegerField(unique=True)
    group_number = models.IntegerField()
    group = models.ForeignKey(Group, models.DO_NOTHING)
    objects = models.Manager()

    class Meta:
        db_table = 'user'

    @staticmethod
    @app.task(name='bot.tasks.get_user')
    def get_user(user_id: int, reply_to, correlation_id):
        user_to_send = None
        try:
            user = User.objects.get(user_id = user_id)
            user_to_send = {
                "id" : user.id,
                "user_id" : user.user_id,
                "group_number": user.group_number,
                "group_id": user.group_id,
            }
        except ObjectDoesNotExist:
            print(f'Возникла ошибка при поиске пользовтаеля с id {user_id}')
        finally:
            result = {'result': user_to_send}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.change_faculty')
    def change_faculty(user_id: int, new_faculty: str, reply_to=None, correlation_id=None):
        try:
            # Получаем ID нового факультета по его названию
            faculty = Faculty.objects.get(name=new_faculty)  # Аналог Faculty.get(Faculty.name == new_faculty) в Peewee

            # Ищем пользователя по user_id
            user = User.objects.get(user_id=user_id)

            # Обновляем название факультета и его ID
            user.faculty = new_faculty  # Сохраняем название факультета (строка)
            user.faculty_id = faculty.id  # Сохраняем ID факультета
            user.save()

            print(f"Факультет пользователя '{user_id}' успешно изменен на '{new_faculty}' (ID: {faculty.id}).")

        except Faculty.DoesNotExist:
            print(f"Ошибка: Факультет '{new_faculty}' не найден.")
        except User.DoesNotExist:
            print(f"Ошибка: Пользователь с ID {user_id} не найден.")
        except Exception as e:
            print(f"Ошибка при изменении факультета: {e}")

        finally:
            # Отправляем пустой словарь в качестве подтверждения выполнения
            asyncio.run(send_response({}, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_all_users_ids')
    def get_all_users_ids(reply_to, correlation_id):
        try:
            user_ids = list(User.objects.values_list('user_id', flat=True))
            result = {'result': user_ids}

            # Отправляем ответ через асинхронную функцию
            asyncio.run(send_response(result, reply_to, correlation_id))

        except Exception as e:
            logging.exception(f"Ошибка в get_all_users_ids: {e}")

    @staticmethod
    @app.task(name='bot.tasks.get_group_number')
    def get_group_number(user_id: int, reply_to=None, correlation_id=None):
        try:
            user = User.objects.get(user_id=user_id)
            group_number = user.group_number
            result = {'result': group_number}
            if reply_to and correlation_id:
                # Если переданы параметры для ответа, отправляем результат через send_response
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                # Если параметры ответа отсутствуют, возвращаем результат
                return result
        except ObjectDoesNotExist:
            raise ValueError(f"Пользователь с идентификатором '{user_id}' не найден")


    @staticmethod
    @app.task(name='bot.tasks.registrate_user')
    def registrate_user(user_id, group_number, reply_to, correlation_id):
        flag = False
        try:
            # Проверяем, существует ли группа
            group = Group.objects.get(group_number = group_number)

            # Создаем запись о пользователе
            User.objects.create(user_id=user_id, group_number=group_number, group_id=group.id)
            flag = True
            print(f"Пользователь '{user_id}' успешно зарегистрирован в группе '{group_number}'.")
        except ObjectDoesNotExist:
            print(f"Группа с номером {group_number} не найдена.")
        except IntegrityError:
            print(f"Пользователь с идентификатором '{user_id}' уже существует в базе данных.")
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.change_group_number')
    def change_group_number(user_id, new_group_number, reply_to, correlation_id):
        flag = False
        try:
            # Проверяем, существует ли новая группа
            new_group = Group.objects.get(group_number = new_group_number)

            # Находим пользователя по ID
            user = User.objects.get(user_id = user_id)

            # Обновляем номер группы и внешний ключ
            user.group_number = new_group_number
            user.group_id = new_group
            user.save()
            flag = True
            print(f"Номер группы пользователя '{user_id}' успешно изменен на '{new_group_number}'.")
        except ObjectDoesNotExist:
            print(f"Группа с номером {new_group_number} не найдена.")
            print(f"Или пользователь с идентификатором '{user_id}' не найден.")
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))