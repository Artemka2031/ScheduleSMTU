from datetime import datetime, timedelta

from peewee import CharField, IntegrityError, DoesNotExist

from ORM.database_declaration_and_exceptions import BaseModel, moscow_tz


class WeekType(BaseModel):
    """
    A class to manage week types in educational institutions.

    Attributes:
        name (CharField): Unique name of the week type.
    """

    name = CharField(unique=True)

    @staticmethod
    def initialize_week_types():
        """
        Initializes the database with predefined week types.
        """
        week_types_data = ['Верхняя неделя', 'Нижняя неделя', 'Обе недели']

        for week_type_name in week_types_data:
            try:
                WeekType.create(name=week_type_name)
                print(f"Week type '{week_type_name}' successfully added.")
            except IntegrityError:
                print(f"Week type '{week_type_name}' already exists in the database.")

    @staticmethod
    def get_week_type_id(week_type_name):
        """
        Returns the ID of a week type by its name.

        Params:
            week_type_name (str): The name of the week type.

        Returns:
            int: The ID of the week type.
        """
        try:
            week_type = WeekType.get(WeekType.name == week_type_name)
            return week_type.id
        except DoesNotExist:
            raise ValueError(f"Week type '{week_type_name}' not found")

    @staticmethod
    def get_current_week():
        """
        Determines the type of the current week based on the current date and week number.

        Returns:
            str: The type of the current week.
        """
        week_number = datetime.now(moscow_tz).isocalendar()[1]
        return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'

    @staticmethod
    def get_tomorrow_week():
        """
        Determines the week type for tomorrow.

        Returns:
            str: The week type for tomorrow.
        """
        tomorrow_date = datetime.now(moscow_tz) + timedelta(days=1)
        week_number = tomorrow_date.isocalendar()[1]
        return 'Верхняя неделя' if week_number % 2 == 0 else 'Нижняя неделя'


class Weekday(BaseModel):
    """
    A class to manage weekdays in educational institutions.

    Attributes:
        name (CharField): Unique name of the weekday.
    """

    name = CharField(unique=True)

    @staticmethod
    def initialize_weekdays():
        """
        Initializes the database with predefined weekdays.
        """
        weekdays_data = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        for weekday_name in weekdays_data:
            try:
                Weekday.create(name=weekday_name)
                print(f"Weekday '{weekday_name}' successfully added.")
            except IntegrityError:
                print(f"Weekday '{weekday_name}' already exists in the database.")

    @staticmethod
    def get_weekday_id(weekday_name):
        """
        Returns the ID of a weekday by its name.

        Params:
            weekday_name (str): The name of the weekday.

        Returns:
            int: The ID of the weekday.
        """
        try:
            weekday = Weekday.get(Weekday.name == weekday_name)
            return weekday.id
        except DoesNotExist:
            raise ValueError(f"Weekday '{weekday_name}' not found")

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
    def get_today():
        """
        Determines today's weekday based on the current date.

        Returns:
            str: The name of today's weekday.
        """
        current_date = datetime.now(moscow_tz)
        try:
            today_weekday = Weekday.get(id=current_date.weekday() + 1)
            return today_weekday.name
        except DoesNotExist:
            raise ValueError("Error determining today's weekday")

    @staticmethod
    def get_tomorrow(current_weekday_name):
        """
        Determines tomorrow's weekday based on the current weekday name.

        Params:
            current_weekday_name (str): The name of the current weekday.

        Returns:
            str: The name of tomorrow's weekday.
        """
        try:
            current_weekday = Weekday.get(Weekday.name == current_weekday_name)
            tomorrow_id = (current_weekday.id % 7) + 1
            tomorrow_weekday = Weekday.get(id=tomorrow_id)
            return tomorrow_weekday.name
        except DoesNotExist:
            raise ValueError("Error determining tomorrow's weekday")


class ClassTime(BaseModel):
    """
    A class to manage class times in educational institutions.

    Attributes:
        start_time (CharField): Start time of the class.
        end_time (CharField): End time of the class.
    """

    start_time = CharField(unique=True)
    end_time = CharField(unique=True)

    @staticmethod
    def initialize_class_times():
        """
        Initializes the database with predefined class times.
        """
        class_times_data = [('08:30', '10:00'), ('10:10', '11:40'), ('11:50', '13:20'), ('14:00', '15:30'),
                            ('15:40', '17:10'), ('17:20', '18:50'), ('19:00', '20:30'), ('20:40', '22:10')]

        for start, end in class_times_data:
            try:
                ClassTime.create(start_time=start, end_time=end)
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
            class_time = ClassTime.get(start_time=start_time, end_time=end_time)
            return class_time.id
        except DoesNotExist:
            raise ValueError(f"Class time from {start_time} to {end_time} not found or invalid.")
