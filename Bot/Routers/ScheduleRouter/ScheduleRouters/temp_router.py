from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Middlewares.authentication_middleware import IsRegMiddleware
from ORM.schedule_information import GroupSchedule, Weekday, WeekType
from ORM.users_info import User
from Bot.Routers.ScheduleRouter.ScheduleRouters.format_functions import format_schedule

tempRouter = Router()

tempRouter.message.middleware(IsRegMiddleware())


@tempRouter.message(F.text == "Сегодня")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    group_number = User.get_group_number(user_id)

    today = Weekday.get_today()

    if today == "Воскресенье":
        await message.answer("Сегодня выходной! 🎉")
        return

    # Получаем данные о расписании
    sorted_schedule = GroupSchedule.get_schedule(group_number, today)

    # Проверяем наличие данных
    if sorted_schedule:

        week_type = WeekType.get_current_week()
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, week_type)
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


@tempRouter.message(F.text == "Завтра")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id

    group_number = User.get_group_number(user_id)

    tomorrow = Weekday.get_tomorrow(Weekday.get_today())

    if tomorrow == "Воскресенье":
        await message.answer("Завтра выходной! 🎉")
        return

    # Получаем данные о расписании
    sorted_schedule = GroupSchedule.get_schedule(group_number, tomorrow)

    # Проверяем наличие данных
    if sorted_schedule:

        week_type = WeekType.get_tomorrow_week()
        # Отправляем отформатированное расписание
        formatted_schedule = format_schedule(sorted_schedule, week_type)
        await message.answer(f"{hbold(f'Расписание {group_number}')}:\n\n{formatted_schedule}")
    else:
        await message.answer("Извините, расписание не найдено.")


