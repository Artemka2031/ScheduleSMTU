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
            return True, "Notification added successfully."
        except DoesNotExist:
            return False, "User not found."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def cancel_notification(user_id):
        try:
            # Поиск всех уведомлений для данного пользователя
            query = Notification.delete().where(Notification.user == user_id)
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
            # Проверка наличия пользователя в таблице
            notification_exists = Notification.select().where(Notification.user == user_id).exists()

            if notification_exists:
                return True, "User has subscription."
            else:
                return False, "User has no subscription."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_all_notifications():
        try:
            user_ids = [{user.user_id: user.notification_time} for user in Notification.select(Notification.user) if
                        user.notification_time]
            return user_ids
        except Exception as e:
            return False, str(e)
