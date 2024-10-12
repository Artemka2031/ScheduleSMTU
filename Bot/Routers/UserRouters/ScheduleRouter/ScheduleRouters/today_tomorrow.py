from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Middlewares.authentication_middleware import IsRegMiddleware
from Bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_schedule
from Bot.RabbitMQProducer.producer_api import send_request_mq


TodayTomorrowRouter = Router()

TodayTomorrowRouter.message.middleware(IsRegMiddleware())


@TodayTomorrowRouter.message(F.text == "Сегодня")
async def schedule_today(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    group_number = await send_request_mq('bot.tasks.get_group_number', [user_id])
    #group_number = BaseUser.get_group_number(user_id)
    today = await send_request_mq('bot.tasks.get_today', [])
    #today = Weekday.get_today()

    if today == "Воскресенье":
        await message.answer("Сегодня выходной! 🎉")
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
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


@TodayTomorrowRouter.message(F.text == "Завтра")
async def schedule_tomorrow(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    group_number = await send_request_mq('bot.tasks.get_group_number', [user_id])
    #group_number = BaseUser.get_group_number(user_id)
    today = await send_request_mq('bot.tasks.get_today', [])

    tomorrow = await send_request_mq('bot.tasks.get_tomorrow', [today])
    #tomorrow = Weekday.get_tomorrow(Weekday.get_today())

    if tomorrow == "Воскресенье":
        await message.answer("Завтра выходной! 🎉")
        return
    sorted_schedule = await send_request_mq('bot.tasks.get_schedule', [group_number, tomorrow])
    # Получаем данные о расписании
    #sorted_schedule = GroupSchedule.get_schedule(group_number, tomorrow)

    # Проверяем наличие данных
    if sorted_schedule:
        week_type = await send_request_mq('bot.tasks.get_tomorrow_week', [])
        #week_type = WeekType.get_tomorrow_week()
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, week_type)
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


