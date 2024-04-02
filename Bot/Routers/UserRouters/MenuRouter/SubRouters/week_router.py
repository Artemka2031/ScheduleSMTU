from datetime import datetime

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText, SendMessage
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram_calendar import SimpleCalendar, get_user_locale, DialogCalendar, CalendarLabels, DialogCalendarCallback

from Bot.Keyboards.menu_kb import create_menu_kb, MenuCallback
from Bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from Bot.Routers.UserRouters.MenuRouter.SubRouters.TeachersRouters.teachers_callback_router import \
    init_dialog_calendar_teacher_month
from Bot.Routers.UserRouters.MenuRouter.menu_state import MenuState
from Bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_schedule, \
    format_dual_week_schedule
from Bot.bot_initialization import bot
from ORM.Tables.SceduleTables.group_schedule import GroupSchedule
from ORM.Tables.SceduleTables.time_tables import WeekType, Weekday
from ORM.Tables.UserTables.user_table import User

WeekScheduleRouter = Router()


@WeekScheduleRouter.callback_query(MenuState.menu_option, MenuCallback.filter(F.operation == "schedule"))
async def call_menu(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await bot(EditMessageText(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Текущий тип недели: {hbold(WeekType.get_current_week())}.\n\n"
                                   f"Выбранная группа: {hbold(User.get_group_number(call.message.chat.id))}\n\n"
                                   f"Выберите тип недели или воспользуйтесь виджетом каледаря:",
                              reply_markup=week_type_kb(back_to_menu=True)))

    await state.set_state(MenuState.week_type)


@WeekScheduleRouter.callback_query(MenuState.week_type, WeekTypeCallback.filter(F.week_type == "Открыть календарь"))
async def open_calendar(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        "Пожалуйста, выберите дату: ",
        reply_markup=await DialogCalendar(locale=await get_user_locale(call.from_user)).start_calendar(
            year=datetime.now().year, month=datetime.now().month)
    )
    await state.set_state(MenuState.group_calendar)


@WeekScheduleRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-YEAR"))
async def init_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                     state: FSMContext):
    current_state = await state.get_state()
    if current_state == MenuState.group_calendar:
        await DialogCalendar(
            locale=await get_user_locale(callback_query.from_user)
        ).process_selection(callback_query, callback_data)
        await state.set_state(MenuState.set_month_group)
    else:
        # Если состояние не совпадает, можем выполнить другие действия или проигнорировать это событие
        await init_dialog_calendar_teacher_month(callback_query, callback_data, state)


@WeekScheduleRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-MONTH"), MenuState.set_month_group)
async def init_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                     state: FSMContext):
    await callback_query.message.edit_text(
        "Пожалуйста, выберите дату: ",
        reply_markup=await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).start_calendar(
            year=datetime.now().year, month=callback_data.month)
    )
    await state.set_state(MenuState.group_calendar)


@WeekScheduleRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-DAY"), MenuState.group_calendar)
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                  state: FSMContext):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:
        await state.update_data(week_type=WeekType.determine_week_type(date))

        week_type = (await state.get_data())['week_type']

        user_id = callback_query.from_user.id
        group_id = User.get_group_number(user_id)
        name_weekday = Weekday.get_weekday_name(date)

        if name_weekday == "Воскресенье":
            await bot(SendMessage(chat_id=callback_query.message.chat.id,
                                  text="В этот день выходной 🎉"))
            await state.clear()
            return

        sorted_schedule = GroupSchedule.get_schedule(group_id, Weekday.get_weekday_name(date))

        if sorted_schedule:
            schedule = format_schedule(sorted_schedule, week_type)
            await bot(
                SendMessage(chat_id=callback_query.message.chat.id,
                            text=f"{hbold(f'Расписание {group_id}')}:\n\n{schedule}"))
        else:
            await bot(SendMessage(chat_id=callback_query.message.chat.id, text="Извините, расписание не найдено."))

    await state.clear()

    await callback_query.message.edit_text(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.update_data(menu_message_id=callback_query.message.message_id)
    await state.set_state(MenuState.menu_option)


@WeekScheduleRouter.callback_query(DialogCalendarCallback.filter(F.act == "CANCEL"))
async def back_to_menu_from_calendar(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await back_to_menu(callback_query, state)


@WeekScheduleRouter.callback_query(MenuState.week_type, WeekTypeCallback.filter(F.week_type == "Назад"))
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_option)


@WeekScheduleRouter.callback_query(MenuState.week_type, WeekTypeCallback.filter())
async def send_choose_week_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    await call.message.edit_text(
        text=f"Выбранный тип недели: {hbold(callback_data.week_type)}.\n\nВыберите день недели:",
        reply_markup=week_day_kb())
    await state.update_data(week_type=callback_data.week_type)
    await state.set_state(MenuState.week_day)


@WeekScheduleRouter.callback_query(MenuState.week_day, WeekDayCallback.filter(F.week_day == "Назад"))
async def back_to_week_type(call: CallbackQuery, state: FSMContext):
    await state.update_data(week_type=None)
    await call.answer()
    # await call.message.edit_text(
    #     text=f"Текущий тип недели: {WeekType.get_current_week()}.\n\n"
    #          f"Выбранная группа: {User.get_group_number(call.from_user.id)}\n\n"
    #          f"Выберите тип недели:",
    #     reply_markup=week_type_kb(back_to_menu=True))
    # await state.set_state(MenuState.week_type)
    await call_menu(call, state)


@WeekScheduleRouter.callback_query(MenuState.week_day, WeekDayCallback.filter())
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
        await bot(
            SendMessage(chat_id=call.message.chat.id, text=f"{hbold(f'Расписание {group_id}')}:\n\n{schedule}"))
    else:
        await bot(SendMessage(chat_id=call.message.chat.id, text="Извините, расписание не найдено."))

    await state.clear()

    await call.message.edit_text(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.update_data(menu_message_id=call.message.message_id)
    await state.set_state(MenuState.menu_option)
