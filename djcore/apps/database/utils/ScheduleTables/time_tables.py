import asyncio
import locale
from datetime import datetime, timedelta
import platform

from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from apps.database.utils.Path.schedule_path_functions import find_group_dir_by_group_number
from djcore.apps.database.utils.config_db import moscow_tz
from djcore.apps.database.utils.send_response import send_response
from djcore.celery_app import app


class WeekType(models.Model):
    name = models.CharField(unique=True, max_length=255)
    objects = models.Manager()

    class Meta:
        db_table = 'weektype'

    @staticmethod
    def initialize_week_types():
        """
        Initializes the database with predefined week types.
        """
        week_types_data = ['Верхняя неделя', 'Нижняя неделя', 'Обе недели']

        for week_type_name in week_types_data:
            try:
                WeekType.objects.create(name=week_type_name)
                print(f"Week type '{week_type_name}' successfully added.")
            except IntegrityError:
                print(f"Week type '{week_type_name}' already exists in the database.")

    @staticmethod
    @app.task(name='bot.tasks.get_week_type_id')
    def get_week_type_id(week_type_name, reply_to=None, correlation_id=None):
        week_type_id = None
        """
        Returns the ID of a week type by its name.

        Params:
            week_type_name (str): The name of the week type.

        Returns:
            int: The ID of the week type.
        """
        try:
            week_type_id = WeekType.objects.get(name=week_type_name).id
        except ObjectDoesNotExist:
            raise ValueError(f"Week type '{week_type_name}' not found")
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result':week_type_id}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return week_type_id

    @staticmethod
    @app.task(name='bot.tasks.get_current_week')
    def get_current_week(reply_to, correlation_id):
        """
        Determines the type of the current week based on the current date and week number.

        Returns:
            str: The type of the current week.
        """
        week_number = datetime.now(moscow_tz).isocalendar()[1]
        if week_number % 2 ==0:
            cur_week = 'Верхняя неделя'
        else:
            cur_week = 'Нижняя неделя'
        #return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'
        result = {'result': cur_week}
        asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.determine_week_type')
    def determine_week_type(date_to_check: str, reply_to, correlation_id):
        """
        Determines the type of the week based on the given date.

        Args:
            date_to_check (datetime): The date to check.

        Returns:
            str: The type of the week for the given date.
        """
        date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d %H:%M:%S')
        week_number = date_to_check.isocalendar()[1]
        if week_number % 2 ==0:
            week_type = 'Верхняя неделя'
        else:
            week_type = 'Нижняя неделя'
        #return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'
        result = {'result': week_type}
        asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_tomorrow_week')
    def get_tomorrow_week(reply_to, correlation_id):
        """
        Determines the week type for tomorrow.

        Returns:
            str: The week type for tomorrow.
        """
        tomorrow_date = datetime.now(moscow_tz) + timedelta(days=1)
        week_number = tomorrow_date.isocalendar()[1]
        if week_number % 2 == 0:
            t_week_type = 'Верхняя неделя'
        else:
            t_week_type = 'Нижняя неделя'
        # return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'
        result = {'result': t_week_type}
        asyncio.run(send_response(result, reply_to, correlation_id))

class Weekday(models.Model):
    name = models.CharField(unique=True, max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'weekday'
    @staticmethod
    def initialize_weekdays():
        """
        Initializes the database with predefined weekdays.
        """
        weekdays_data = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        for weekday_name in weekdays_data:
            try:
                Weekday.objects.create(name=weekday_name)
                print(f"Weekday '{weekday_name}' successfully added.")
            except IntegrityError:
                print(f"Weekday '{weekday_name}' already exists in the database.")

    @staticmethod
    @app.task(name='bot.tasks.get_weekday_name')
    def get_weekday_name(date: str, reply_to, correlation_id):
        """
        Returns the name of the weekday based on the given date.

        Args:
            date (datetime): The date to check.

        Returns:
            str: The name of the weekday for the given date.
        """
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        system = platform.system()

        # Настраиваем локаль в зависимости от ОС
        if system == 'Windows':
            try:
                locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
            except locale.Error as e:
                print(f"Locale error on Windows: {e}")
                locale.setlocale(locale.LC_TIME, '')
        else:
            try:
                locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
            except locale.Error as e:
                print(f"Locale error on Linux: {e}")
                locale.setlocale(locale.LC_TIME, '')

        # Получаем название дня недели
        day_name = date.strftime("%A")

        # Возвращаем результат с корректной кодировкой
        result = {'result': day_name.capitalize()}
        asyncio.run(send_response(result, reply_to, correlation_id))

    @staticmethod
    @app.task(name='bot.tasks.get_weekday_id')
    def get_weekday_id(weekday_name, reply_to=None, correlation_id=None):
        weekday_id = None
        """
        Returns the ID of a weekday by its name.

        Params:
            weekday_name (str): The name of the weekday.

        Returns:
            int: The ID of the weekday.
        """
        try:
            weekday_id = Weekday.objects.get(name=weekday_name).id
        except ObjectDoesNotExist:
            raise ValueError(f"Weekday '{weekday_name}' not found")
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': weekday_id}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return weekday_id

    @staticmethod
    def get_order(day_name: str) -> int:
        """
        Determines the order of a given weekday.

        Params:
            day_name (str): The name of the weekday.

        Returns:
            int: The order of the weekday, starting from Monday as 1.
        """
        order = {
            'Понедельник': 1,
            'Вторник': 2,
            'Среда': 3,
            'Четверг': 4,
            'Пятница': 5,
            'Суббота': 6,
            'Воскресенье': 7
        }
        return order.get(day_name, 0)

    @staticmethod
    @app.task(name='bot.tasks.get_today')
    def get_today(reply_to, correlation_id):
        """
        Determines today's weekday based on the current date.

        Returns:
            str: The name of today's weekday.
        """
        current_date = datetime.now(moscow_tz)
        try:
            today_weekday = Weekday.objects.get(id=current_date.weekday() + 1)
            name = today_weekday.name
            result = {'result': name}
            asyncio.run(send_response(result, reply_to, correlation_id))
        except ObjectDoesNotExist:
            raise ValueError("Error determining today's weekday")


    @staticmethod
    @app.task(name='bot.tasks.get_tomorrow')
    def get_tomorrow(current_weekday_name, reply_to, correlation_id):
        """
        Determines tomorrow's weekday based on the current weekday name.

        Params:
            current_weekday_name (str): The name of the current weekday.

        Returns:
            str: The name of tomorrow's weekday.
        """
        try:
            current_weekday = Weekday.objects.get(name=current_weekday_name)
            tomorrow_id = (current_weekday.id % 7) + 1
            tomorrow_weekday = Weekday.objects.get(id=tomorrow_id)
            t_name = tomorrow_weekday.name
            result = {'result': t_name}
            asyncio.run(send_response(result, reply_to, correlation_id))
        except ObjectDoesNotExist:
            raise ValueError("Error determining tomorrow's weekday")

class ClassTime(models.Model):
    start_time = models.CharField(unique=True, max_length=255)
    end_time = models.CharField(unique=True, max_length=255)
    objects = models.Manager()
    class Meta:
        db_table = 'classtime'

    @staticmethod
    def initialize_class_times():
        """
        Initializes the database with predefined class times.
        """
        class_times_data = [('08:30', '10:00'), ('10:10', '11:40'), ('11:50', '13:20'), ('14:00', '15:30'),
                            ('15:40', '17:10'), ('17:20', '18:50'), ('19:00', '20:30'), ('20:40', '22:10')]

        for start, end in class_times_data:
            try:
                ClassTime.objects.create(start_time=start, end_time=end)
                print(f"Class time from {start} to {end} successfully added.")
            except IntegrityError:
                print(f"Class time from {start} to {end} already exists in the database.")

    @staticmethod
    def get_class_time_id(time_range):
        """
        Returns the ID of a class time by its start and end time.

        Params:
            time_range (str): The time range in the format "start_time-end_time".

        Returns:
            int: The ID of the class time.
        """
        start_time, end_time = map(lambda x: x.strip(), time_range.split('-'))

        try:
            class_time = ClassTime.objects.get(start_time=start_time, end_time=end_time)
            return class_time.id
        except ObjectDoesNotExist:
            raise ValueError(f"Class time from {start_time} to {end_time} not found or invalid.")
    
    @staticmethod
    @app.task(name='bot.tasks.get_all_pare_start_time')
    def get_all_pare_start_time(reply_to = None, correlation_id = None):
        return_class_time = {}
        try:
            class_times = ClassTime.objects.all()

            return_class_time = {}
            for pare in class_times:
                return_class_time[pare.start_time] = pare.id

        except ClassTime.DoesNotExist:
            raise ValueError("Class times not found or invalid.")

        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': return_class_time}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return return_class_time

    @staticmethod
    @app.task(name="bot.tasks.get_time_text_by_id")
    def get_time_text_by_id(time_id:int, reply_to = None, correlation_id = None):
        class_time = None
        try:
            class_time = ClassTime.objects.get(id=time_id).start_time
        except ObjectDoesNotExist:
            print("Class times not found or invalid.")
        finally:
            if reply_to is not None and correlation_id is not None:
                result = {'result': class_time}
                asyncio.run(send_response(result, reply_to, correlation_id))
            else:
                return class_time