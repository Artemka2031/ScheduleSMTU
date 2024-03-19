import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ORM.Tables.SceduleTables.time_tables import Weekday


async def check_vuc_schedule():
    current_day = Weekday.get_today()  # Получаем текущий день

    new_file_ids = 'ORM/VUC/NewSchedule/new_file_ids.txt'

    os.makedirs('ORM/VUC/OldSchedule/', exist_ok=True)
    old_file_ids = 'ORM/VUC/OldSchedule/old_file_ids.txt'

    if not os.path.exists(old_file_ids):
        with open(old_file_ids, 'w'):  # Создаем пустой файл, если его нет
            pass

    if current_day == "Суббота":
        with open(new_file_ids, 'r+') as file:
            lines = file.readlines()
            old_id = lines[0]  # Сохраняем первую строку в переменную old_id
            lines[0] = lines[1]  # Первую строку делаем равной содержимому второй строки
            lines[1] = '\n'  # Вторую строку очищаем
            file.seek(0)
            file.writelines(lines)  # Перезаписываем файл
            file.truncate()

        with open(old_file_ids, 'r+') as old_file:
            if len(old_id) > 0:
                old_content = old_file.read()
                old_file.seek(0)
                old_file.write(old_id + old_content)


async def vuc_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_vuc_schedule, 'cron', hour=0, minute=0)
    scheduler.start()
