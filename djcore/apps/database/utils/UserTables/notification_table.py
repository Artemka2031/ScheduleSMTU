import asyncio

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from djcore.apps.database.utils.UserTables.user_table import User
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class Notification(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    notification_time = models.TimeField()
    objects = models.Manager()

    class Meta:
        db_table = 'notification'
    @staticmethod
    @app.task(name='bot.tasks.add_notification')
    def add_notification(user_id, notification_time, reply_to, correlation_id):
        flag = False
        try:
            # Поиск пользователя по ID
            user = User.objects.get(user_id = user_id)

            # Добавление новой записи об уведомлении
            Notification.objects.create(user=user, notification_time=notification_time)

            # notification.save()

            flag = True
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            print(str(e))
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.update_notification')
    def update_notification(user_id, new_notification_time, reply_to, correlation_id):
        flag = False
        try:
            # Поиск уведомления для данного пользователя

            user = User.objects.get(user_id = user_id)
            notification = Notification.objects.get(user = user)

            # Обновление времени уведомления
            notification.notification_time = new_notification_time
            notification.save()
            flag = True
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            print(str(e))
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.cancel_notification')
    def cancel_notification(user_id, reply_to, correlation_id):
        flag = False
        try:
            user = User.objects.get(user_id = user_id)
            # Поиск всех уведомлений для данного пользователя
            notification_to_del = Notification.objects.get(user=user)
            notification_to_del.delete()
             # Выполнение запроса на удаление и получение количества удаленных записей

            flag = True
            print(f"Successfully cancelled notifications for user - {user}.")

        except Exception as e:
            print(str(e))
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.has_subscription')
    def has_subscription(user_id, reply_to, correlation_id):
        flag = False
        try:
            user = User.objects.get(user_id = user_id)

            user_notifications_exists = Notification.objects.filter(user=user).exists()

            if user_notifications_exists:
                flag = True
        except Exception as e:
            print(str(e))
        finally:
            result = {'result': flag}
            asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_all_notifications')
    def get_all_notifications(reply_to, correlation_id):
        user_notifications = {}
        try:
            # user_notifications = {user.user_id: user.notification_time for user in
            #                       Notification.select(Notification.user) if user.notification_time}
            notifications = Notification.objects.values_list('user', 'notification_time')

            # notifications = Notification.select(Notification.user, Notification.notification_time)
            for user, notification_time in notifications:
                user_notifications[user.user_id] = notification_time

        except Exception as e:
            user_notifications = False
            print(str(e))
        finally:
            result = {'result': user_notifications}
            asyncio.run(send_response(result, reply_to, correlation_id))