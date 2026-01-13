import asyncio
import logging

from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.utils.ScheduleTables.group_tables import Faculty
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class AdminUser(models.Model):
    user_id = models.IntegerField(unique=True)
    faculty = models.CharField(max_length=255)
    faculty_id = models.ForeignKey(Faculty, models.DO_NOTHING)
    objects = models.Manager()

    class Meta:
        db_table = 'user_admin_bot'

    @staticmethod
    @app.task(name='admin_bot.tasks.get_user')
    def get_user(user_id: int, reply_to, correlation_id):
        user_to_send = None
        try:
            logging.info(f"Запрос пользователя с user_id: {user_id}")
            user = AdminUser.objects.get(user_id=user_id)
            logging.info(f"Найден пользователь: {user}")
            user_to_send = {
                "id": user.id,
                "user_id": user.user_id,
                "faculty": user.faculty,
                "faculty_id": user.faculty_id.id,  # передаем только id
            }
        except ObjectDoesNotExist:
            logging.warning(f"Пользователь с user_id {user_id} не найден")
        except Exception as e:
            logging.exception("Ошибка при получении пользователя")
        finally:
            result = {'result': user_to_send}
            logging.info(f"Отправляем результат: {result}")
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='admin_bot.tasks.change_faculty')
    def change_faculty(user_id: int, new_faculty: str, reply_to=None, correlation_id=None):
        try:
            # Получаем ID нового факультета по его названию
            faculty = Faculty.objects.get(name=new_faculty)  # Аналог Faculty.get(Faculty.name == new_faculty) в Peewee

            # Ищем пользователя по user_id
            user = AdminUser.objects.get(user_id=user_id)

            # Обновляем название факультета и его ID
            user.faculty = new_faculty  # Сохраняем название факультета (строка)
            user.faculty_id = faculty  # Сохраняем ID факультета
            user.save()

            print(f"Факультет пользователя '{user_id}' успешно изменен на '{new_faculty}' (ID: {faculty.id}).")

        except Faculty.DoesNotExist:
            print(f"Ошибка: Факультет '{new_faculty}' не найден.")
        except AdminUser.DoesNotExist:
            print(f"Ошибка: Пользователь с ID {user_id} не найден.")
        except Exception as e:
            print(f"Ошибка при изменении факультета: {e}")

        finally:
            # Отправляем пустой словарь в качестве подтверждения выполнения
            asyncio.run(send_response({}, reply_to, correlation_id))

    @staticmethod
    @app.task(name='admin_bot.tasks.get_all_users_ids')
    def get_all_users_ids(reply_to, correlation_id):
        user_ids = []
        try:
            # Используем sync_to_async для выполнения синхронного запроса к базе данных асинхронно
            user_ids = list(AdminUser.objects.values_list('user_id', flat=True))
        except Exception as e:
            logging.exception(f"Ошибка в get_all_users_ids: {e}")
        finally:
            result = {'result': user_ids}
            # Отправляем ответ через асинхронную функцию
            asyncio.run(send_response(result, reply_to, correlation_id))

    # @staticmethod
    # @app.task(name='admin_bot.tasks.get_group_number')
    # def get_group_number(user_id: int, reply_to=None, correlation_id=None):
    #     try:
    #         user = AdminUser.objects.get(user_id=user_id)
    #         group_number = user.group_number
    #         result = {'result': group_number}
    #         if reply_to and correlation_id:
    #             # Если переданы параметры для ответа, отправляем результат через send_response
    #             asyncio.run(send_response(result, reply_to, correlation_id))
    #         else:
    #             # Если параметры ответа отсутствуют, возвращаем результат
    #             return result
    #     except ObjectDoesNotExist:
    #         raise ValueError(f"Пользователь с идентификатором '{user_id}' не найден")
    #

    @staticmethod
    @app.task(name='admin_bot.tasks.get_faculty_id')
    def get_faculty_id(user_id: int, reply_to=None, correlation_id=None):
        faculty_id = None
        try:
            faculty_id = AdminUser.objects.get(user_id=user_id).faculty_id.id
        except ObjectDoesNotExist:
            print('ObjectDoesNotExist')
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': faculty_id}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return faculty_id

    @staticmethod
    @app.task(name='admin_bot.tasks.registrate_user')
    def registrate_user(user_id, faculty, faculty_id, reply_to=None, correlation_id=None):
        flag = False
        try:
            # Проверяем, существует ли группа
            faculty = Faculty.objects.get(name = faculty)

            # Создаем запись о пользователе
            AdminUser.objects.create(user_id=user_id, faculty=faculty.name, faculty_id=faculty)
            flag = True
            print(f"Пользователь '{user_id}' успешно зарегистрирован в группе '{faculty.name}'.")
        except ObjectDoesNotExist:
            print(f"Факультет {faculty} не найден.")
        except IntegrityError:
            print(f"Пользователь с идентификатором '{user_id}' уже существует в базе данных.")
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='admin_bot.tasks.get_faculty_name')
    def get_faculty_name(user_id: int, reply_to=None, correlation_id=None):
        users_faculty = None
        try:
            users_faculty = AdminUser.objects.get(user_id=user_id).faculty
        except ObjectDoesNotExist:
            print(f"Пользователь с user_id {user_id} не найден")

        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': users_faculty}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return users_faculty

    @staticmethod
    @app.task(name='admin_bot.tasks.get_faculty_id')
    def get_faculty_id(user_id: int, reply_to=None, correlation_id=None):
        users_faculty_id = None
        try:
            users_faculty_id = AdminUser.objects.get(user_id=user_id).faculty_id.id
        except ObjectDoesNotExist:
            print(f"Пользователь с user_id {user_id} не найден")
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': users_faculty_id}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return users_faculty_id