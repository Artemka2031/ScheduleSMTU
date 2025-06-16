from datetime import datetime

from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Bot.RabbitMQProducer.producer_api import send_request_mq
from Bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_schedule
from Bot.bot_initialization import bot


# Функция для отправки уведомлений пользователям в заданное время
async def send_notifications():
    current_hour = datetime.now().hour   # Получаем текущий час
    notifications = await send_request_mq('bot.tasks.get_all_notifications', [])
    #notifications = Notification.get_all_notifications()  # Получаем все уведомления
    for user_id, notification_time in notifications.items():
        if int(notification_time) == current_hour:
            group_number = await send_request_mq('bot.tasks.get_group_number', [user_id])
            #group_number = BaseUser.get_group_number(user_id)
            today = await send_request_mq('bot.tasks.get_today', [])
            #today = Weekday.get_today()

            if today == "Воскресенье":
                await bot.send_message(text="Сегодня выходной! 🎉", chat_id=user_id)
                return
            sorted_schedule = await send_request_mq('bot.tasks.get_schedule', [group_number, today])
            # Получаем данные о расписании
            #sorted_schedule = GroupSchedule.get_schedule(group_number, today)
            # Проверяем наличие данных
            if sorted_schedule:
                week_type = await send_request_mq('bot.tasks.get_current_week', [])
                #week_type = WeekType.get_current_week()
                # Отправляем отформатированное расписание
                formatted_schedule = format_schedule(sorted_schedule, week_type)
                await bot.send_message(text=f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}",
                                               chat_id=user_id)
            # else:
            #     await bot.send_message(text="Извините, расписание не найдено.", chat_id=user_id)


# Запуск асинхронного цикла для выполнения планировщика
async def notification_scheduler():
    scheduler = AsyncIOScheduler()
    for hour in range(0, 10):
        scheduler.add_job(send_notifications, 'cron', hour=hour, minute=0)
    scheduler.start()



