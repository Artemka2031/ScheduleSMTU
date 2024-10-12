import asyncio
import logging

from djcore.apps.parser.utils.Parsers import fetch_employees_data, set_schedule_data
from djcore.celery_app import app

@app.task(bind=True, max_retries=3, default_retry_delay=5)
def schedule_parse(self):
    try:
        asyncio.run(set_schedule_data())
        logging.info("Парсинг расписания завершён успешно и сообщение отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        self.retry(exc=e)

@app.task(bind=True, max_retries=3, default_retry_delay=5)
def employees_parse(self):
    try:
        asyncio.run(fetch_employees_data())

        logging.info("Парсинг сотрудников завершён успешно и сообщение отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        self.retry(exc=e)