from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from Bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from Bot.Middlewares import IsRegMiddleware
from Bot.Routers.ScheduleRouters.temp_router import format_schedule, format_dual_week_schedule
from ORM.Tables.group_schedule import WeekType, GroupSchedule
from ORM.users_info import User

WeekScheduleRouter = Router()

WeekScheduleRouter.message.middleware(IsRegMiddleware())


class WeekScheduleState(StatesGroup):
    menu_message_id = State()
    week_type = State()
    week_day = State()


@WeekScheduleRouter.message(Command("week_schedule"))
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WeekScheduleState.week_type)

    sent_message = await message.answer(
        text=f"Текущий тип недели: {WeekType.get_current_week()}.\n\nВыбранная группа: {User.get_group_number(message.from_user.id)}\n\nВыберите тип недели:",
        reply_markup=week_type_kb())

    await state.update_data(menu_message_id=sent_message.message_id)
    await state.set_state(WeekScheduleState.week_type)


@WeekScheduleRouter.callback_query(WeekScheduleState.week_type, WeekTypeCallback.filter())
async def send_choose_week_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    await call.message.edit_text(
        text=f"Выбранный тип недели: {callback_data.week_type}.\n\nВыберите день недели:",
        reply_markup=week_day_kb())
    await state.update_data(week_type=callback_data.week_type)
    await state.set_state(WeekScheduleState.week_day)


@WeekScheduleRouter.callback_query(WeekScheduleState.week_day, WeekDayCallback.filter())
async def send_day_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    await call.answer()

    week_type = (await state.get_data())['week_type']

    user_id = call.from_user.id
    group_id = User.get_group_number(user_id)

    sorted_schedule = GroupSchedule.get_schedule(group_id, callback_data.week_day)
    if sorted_schedule:
        if week_type == "Обе недели":
            schedule = format_dual_week_schedule(sorted_schedule)
        else:
            schedule = format_schedule(sorted_schedule, week_type)

        await call.message.edit_text(f"{hbold(f'Расписание {group_id}')}:\n\n{schedule}")
    else:
        await call.message.edit_text("Извините, расписание не найдено.")

    await state.clear()
