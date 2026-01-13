from django.core.management.base import BaseCommand
from djcore.apps.parser.tasks import schedule_parse

class Command(BaseCommand):
    help = 'Парсит сайт вручную'

    def handle(self, *args, **options):
        schedule_parse.delay()
        self.stdout.write(self.style.SUCCESS('Запустили Celery-задачу parse_data_task'))