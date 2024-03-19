from peewee import ForeignKeyField, TimeField, DoesNotExist

from ORM.Tables.UserTables.user_table import User
from ORM.database_declaration_and_exceptions import BaseModel, db


class Notification(BaseModel):
    user = ForeignKeyField(User, backref='notifications')
    notification_time = TimeField()

    class Meta:
        database = db

    @staticmethod
    def add_notification(user_id, notification_time):
        try:
            # Поиск пользователя по ID
            user = User.get(User.user_id == user_id)

            # Добавление новой записи об уведомлении
            notification = Notification.create(user=user, notification_time=notification_time)

            notification.save()

            return True
        except DoesNotExist:
            return False
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_notification(user_id, new_notification_time):
        try:
            # Поиск уведомления для данного пользователя

            user = User.get(User.user_id == user_id)
            notification = Notification.get(Notification.user == user)

            # Обновление времени уведомления
            notification.notification_time = new_notification_time
            notification.save()

            return True
        except DoesNotExist:
            return False
        except Exception as e:
            return False

    @staticmethod
    def cancel_notification(user_id):
        try:
            user = User.get(User.user_id == user_id)
            # Поиск всех уведомлений для данного пользователя
            query = Notification.delete().where(Notification.user == user)
            num_deleted = query.execute()  # Выполнение запроса на удаление и получение количества удаленных записей

            if num_deleted > 0:
                return True, f"Successfully cancelled {num_deleted} notifications."
            else:
                return False, "No notifications found to cancel."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def has_subscription(user_id):
        try:
            user = User.get(User.user_id == user_id)
            notification_exists = Notification.select().where(Notification.user == user).exists()

            if notification_exists:
                return True
            else:
                return False
        except Exception as e:
            return False

    @staticmethod
    def get_all_notifications():
        try:
            # user_notifications = {user.user_id: user.notification_time for user in
            #                       Notification.select(Notification.user) if user.notification_time}
            user_notifications = {}
            notifications = Notification.select(Notification.user, Notification.notification_time)
            for notification in notifications:
                user_id = notification.user.user_id
                user_notifications[user_id] = notification.notification_time

            return user_notifications
        except Exception as e:
            return False, str(e)
