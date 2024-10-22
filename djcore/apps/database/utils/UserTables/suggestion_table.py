import asyncio
import logging
from datetime import datetime

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.utils.UserTables.user_table import User
from djcore.apps.database.utils.config_db import moscow_tz
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class Suggestion(models.Model):
    user = models.ForeignKey("User", models.DO_NOTHING, default='')
    suggestion = models.TextField()
    date = models.DateField()
    closed_date = models.DateField(default=None, null=True, blank=True)
    closed_text = models.TextField(default="", null=True)
    objects = models.Manager()
    class Meta:
        managed = True
        db_table = 'suggestion'

    @staticmethod
    @app.task(name='bot.tasks.add_suggestion')
    def add_suggestion(user_id, suggestion: str, reply_to, correlation_id):
        flag = False
        try:
            user = User.objects.get(user_id = user_id)
            # Создаем запись в таблице Suggestion
            Suggestion.objects.create(user=user, suggestion=suggestion, date=datetime.now(moscow_tz).date())
            print("Предложение успешно добавлено.")
            flag = True
        # except DoesNotExist:
        #     print(f"Пользователь с user_id {user_id} не найден.")
        # except IntegrityError:
        #     print(f"Предложение от пользователя {user_id} уже существует в базе данных.")
        except Exception as e:
            print(f"Произошла ошибка при добавлении предложения: {e}")
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_user_suggestions_count')
    def get_user_suggestions_count(user_id, reply_to, correlation_id):
        count = 0
        try:
            # Получаем текущую дату
            current_date = datetime.now(moscow_tz).date()
            user = User.objects.get(user_id = user_id)
            count = Suggestion.objects.filter(user=user, date=current_date).count()
            # Используем count для подсчета строк по заданным условиям
            # count = Suggestion.select().where(
            #     (Suggestion.user_id == User.get_user(user_id)) &  # Фильтр по пользователю
            #     (Suggestion.date == current_date)  # Фильтр по текущей дате
            # ).count()

            count = count
        except ObjectDoesNotExist:
            print(f"Пользователь с user_id {user_id} не найден.")
        finally:
            result = {'result': count}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_user_suggestion')
    def get_user_suggestion(reply_to, correlation_id):
        user_suggestions = {}
        try:
            suggestions = Suggestion.objects.filter(closed_text='').all()
            #suggestions = Suggestion.select().where(Suggestion.closed_text == '')

            for suggestion in suggestions:
                user_id = suggestion.user.user_id
                suggestion_id = suggestion.id
                if user_id not in user_suggestions:
                    user_suggestions[user_id] = {}  # Создаем вложенный словарь для каждого user_id
                user_suggestions[user_id][suggestion_id] = suggestion.suggestion

        except ObjectDoesNotExist:
            print("Не найдено предложений.")
        finally:
            result = {'result': user_suggestions}
            asyncio.run(send_response(result, reply_to, correlation_id))


    @staticmethod
    @app.task(name='bot.tasks.process_admin_response')
    def process_admin_response(user_id, suggestion_id: int, admin_response_date: str,
                               admin_response_text: str, reply_to, correlation_id):
        flag = None
        try:
            admin_response_date = datetime.strptime(admin_response_date, '%Y-%m-%d').date()

            user = User.objects.get(user_id = user_id)
            suggestion_instance = Suggestion.objects.get(user = user, id = suggestion_id)
            suggestion_instance.closed_date = admin_response_date
            suggestion_instance.closed_text = admin_response_text
            suggestion_instance.save()
            logging.info("Дата и ответ администратора успешно заполнены.")
            flag = 'success'
        except ObjectDoesNotExist:
            print(f"Предложение от пользователя с user_id {user_id} и текстом {suggestion_id} не найдено.")
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))