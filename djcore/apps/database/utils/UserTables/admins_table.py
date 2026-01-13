import asyncio

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class Admins(models.Model):
    admin_id = models.BigIntegerField(unique=True, default=0)
    objects = models.Manager()

    class Meta:
        db_table = 'admins'

    @staticmethod
    @app.task(name='bot.tasks.get_all_admins')
    def get_all_admins(reply_to, correlation_id):
        admins = []
        try:
            # Извлечение всех user_id администраторов
            admins = list(Admins.objects.values_list('admin_id', flat=True))

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            print(str(e))# Если произошла ошибка, возвращаем ошибку
        finally:
            result = {'result':admins}
            asyncio.run(send_response(result, reply_to, correlation_id))