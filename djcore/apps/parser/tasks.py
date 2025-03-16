import asyncio
import logging
from djcore.apps.create_database import refresh_database

from djcore.apps.parser.utils.Parsers import fetch_employees_data, set_schedule_data
from djcore.celery_app import app


@app.task(name='parser.tasks.schedule_employees_parse')
def schedule_parse():
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(set_schedule_data())
        loop.run_until_complete(fetch_employees_data())
        loop.close()
        refresh_database()
        logging.info("Парсинг расписания и сотрудников завершён успешно и сообщение отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")