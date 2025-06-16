# your_project/celery_app.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcore.settings')

app = Celery('djcore')

# app.conf.task_routes = {
#     # 'parser.tasks.schedule_parse': {'queue': 'celery_queue'},
#     # 'parser.tasks.employees_parse': {'queue': 'celery_queue'},
#     'bot.tasks.get_group_id': {'queue': 'bot_queue'},
#     'bot.tasks.get_all_users_ids':{'queue': 'bot_queue'}
# }

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
