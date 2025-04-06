from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import callback_data
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold, hitalic
from aiogram_calendar import DialogCalendar, get_user_locale, DialogCalendarCallback

from admin_bot.Keyboards.group_list_inl_kb import group_list_kb, GroupListCallback
from admin_bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from admin_bot.Middlewares.authentication_middleware import IsRegMiddleware
from admin_bot.Keyboards.classtime_inl_kb import classtime_kb, ClassTimeCallback
from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_schedule, \
    format_groups_list
from admin_bot.RabbitMQProducer.producer_api import send_request_mq


class ByTimeState(StatesGroup):
    group = State()
    class_time = State()
    messages_to_delete = State()
    calendar = State()
    set_month_calendar = State()
    menu = State()
    week_type = State()
    week_day = State()


ScheduleByTimeRouter = Router()
ScheduleByTimeRouter.message.middleware(IsRegMiddleware())


@ScheduleByTimeRouter.message(F.text == 'По времени')
async def schedule_groups_by_time(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f'Выберите из списка время начала {hitalic("интересующей пары")}: ',
        parse_mode=ParseMode.HTML,
        reply_markup=await classtime_kb()
    )
    await state.set_state(ByTimeState.class_time)


# @ScheduleByTimeRouter.callback_query(ByTimeState.class_time, ClassTimeCallback.filter(F.classtime_id == 'cancel'))
# async def cancel_set_group_list(call: CallbackQuery, state: FSMContext, callback_data: ClassTimeCallback):
#     await call.answer()
#     try:
#         await call.bot.delete_messages(
#             chat_id=call.from_user.id,
#             message_ids=[call.message.message_id, call.message.message_id - 1]
#         )
#     except Exception as e:
#         print(e)
#     await state.clear()
#
#
# @ScheduleByTimeRouter.callback_query(ByTimeState.class_time, ClassTimeCallback.filter())
# async def set_group_list(call: CallbackQuery, state: FSMContext, callback_data: ClassTimeCallback):
#     await call.answer()
#     if isinstance(callback_data, str):
#         class_time_id = callback_data
#     else:
#         class_time_id = callback_data.classtime_id
#
#     class_time_text = await send_request_mq('bot.tasks.get_time_text_by_id', [class_time_id])
#     # Обновляем состояние: сохраняем выбранное время; остальные данные (group, week_type) остаются, если уже есть
#     await state.update_data(class_time=class_time_id)
#     await call.message.edit_text(
#         text=f'Выбранное время: {hbold(str(class_time_text))}\nВыберите из списка номер группы, пару которой хотите посмотреть',
#         parse_mode=ParseMode.HTML,
#         reply_markup=await group_list_kb(call.from_user.id, class_time_id)
#     )
#     await state.set_state(ByTimeState.group)


@ScheduleByTimeRouter.callback_query(ByTimeState.class_time, ClassTimeCallback.filter(F.classtime_id == 'cancel'))
async def cancel_get_calendar(call: CallbackQuery, state: FSMContext, callback_data: ClassTimeCallback):
    await call.answer()
    try:
        await call.bot.delete_messages(chat_id=call.from_user.id, message_ids=[call.message.message_id])
    except Exception as e:
        print(e)
    # Переходим заново к выбору времени
    await schedule_groups_by_time(call.message, state)


@ScheduleByTimeRouter.callback_query(ByTimeState.class_time, ClassTimeCallback.filter())
async def choose_way_to_navigate(call: CallbackQuery, state: FSMContext, callback_data: ClassTimeCallback):
    await call.answer()
    # Сохраняем выбранную группу
    if isinstance(callback_data, str):
        class_time_id = callback_data
    else:
        class_time_id = callback_data.classtime_id

    class_time_text = await send_request_mq('bot.tasks.get_time_text_by_id', [class_time_id])
    # Обновляем состояние: сохраняем выбранное время; остальные данные (group, week_type) остаются, если уже есть
    await state.update_data(class_time=class_time_id)


    # group_number = await send_request_mq('admin_bot.tasks.get_group_number', [group_id])
    current_week = await send_request_mq('bot.tasks.get_current_week', [])
    await call.message.edit_text(
        text=f"📅 Текущий тип недели: {hbold(current_week)}\n\n"
             f"🕘 Выбранное время: {hbold(class_time_text)}\n\n"
             f"👇 Выбери тип недели или воспользуйся виджетом календаря для выбора конкретной даты!",
        reply_markup=week_type_kb(back_to_menu=True),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(ByTimeState.menu)


@ScheduleByTimeRouter.callback_query(ByTimeState.menu, WeekTypeCallback.filter(F.week_type == "Открыть календарь"))
async def get_calendar(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(locale=await get_user_locale(call.from_user)).start_calendar(
            year=datetime.now().year, month=datetime.now().month)
    )
    data = (await state.get_data()).get("messages_to_delete", [])
    data.append(call.message.message_id)
    await state.update_data(messages_to_delete=data)
    await state.set_state(ByTimeState.calendar)


@ScheduleByTimeRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-YEAR"))
async def init_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    current_state = await state.get_state()
    if current_state == ByTimeState.calendar:
        await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(callback_query, callback_data)
        await state.set_state(ByTimeState.set_month_calendar)


@ScheduleByTimeRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-MONTH"), ByTimeState.set_month_calendar)
async def process_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).start_calendar(
            year=datetime.now().year,
            month=callback_data.month
        )
    )
    await state.set_state(ByTimeState.calendar)


@ScheduleByTimeRouter.callback_query(ByTimeState.calendar, DialogCalendarCallback.filter(F.act == "SET-DAY"))
async def return_pare_for_group(call: CallbackQuery, state: FSMContext, callback_data: DialogCalendarCallback):
    selected, date = await DialogCalendar(locale=await get_user_locale(call.from_user)).process_selection(call, callback_data)
    user_id = call.from_user.id

    if selected:
        week_type = await send_request_mq('bot.tasks.determine_week_type', [str(date)])
        name_weekday = await send_request_mq('bot.tasks.get_weekday_name', [str(date)])
        data = await state.get_data()
        # Проверяем наличие необходимых ключей
        class_time = data.get('class_time')
        #group_id = data.get('group')
        if not class_time:
            await call.message.answer("Некоторые данные отсутствуют. Пожалуйста, начните заново.")
            await state.clear()
            return

        #group_number = await send_request_mq('admin_bot.tasks.get_group_number', [group_id])
        faculty_id = await send_request_mq('admin_bot.tasks.get_faculty_id', [user_id])


        pares_for_groups_in_selected_time = await send_request_mq('bot.tasks.filter_groups_by_pare_time', [faculty_id, class_time, name_weekday])

        #sorted_schedule_pare = await send_request_mq('bot.tasks.get_pare_for_group', [group_id, class_time, name_weekday])
        if pares_for_groups_in_selected_time:
            formatted_list = await format_groups_list(pares_for_groups_in_selected_time, week_type, name_weekday, class_time)
            if formatted_list:
                await call.message.answer(formatted_list, parse_mode=ParseMode.HTML)
            else:
                await call.message.answer(f"Расписание для групп на этот день и в это время не найдено")

    messages_data = (await state.get_data()).get("messages_to_delete", [])
    try:
        for message_id in messages_data:
            await call.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)
    await state.clear()


@ScheduleByTimeRouter.callback_query(DialogCalendarCallback.filter(F.act == "CANCEL"))
async def back_to_menu_from_calendar(callback_query: CallbackQuery, state: FSMContext):
    # При отмене календаря переходим обратно к выбору времени
    data = await state.get_data()
    class_time = data.get('class_time')
    if not class_time:
        await callback_query.message.answer("Данные отсутствуют. Пожалуйста, начните заново.")
        await state.clear()
        return
    await schedule_groups_by_time(callback_query, state, class_time)


@ScheduleByTimeRouter.callback_query(ByTimeState.menu, WeekTypeCallback.filter(F.week_type == "Назад"))
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_time = data.get('class_time')
    if not class_time:
        await call.message.answer("Данные отсутствуют. Пожалуйста, начните заново.")
        await state.clear()
        return
    await schedule_groups_by_time(call, state, class_time)


@ScheduleByTimeRouter.callback_query(ByTimeState.menu, WeekTypeCallback.filter())
async def send_choose_week_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    actual_cb = callback_data.week_type
    await call.message.edit_text(
        text=f"🔄 Выбранный тип недели: {hbold(actual_cb)}.\n\n👉 Теперь выбери день недели:",
        parse_mode=ParseMode.HTML,
        reply_markup=week_day_kb()
    )
    await state.update_data(week_type=actual_cb)
    await state.set_state(ByTimeState.week_day)


@ScheduleByTimeRouter.callback_query(ByTimeState.week_day, WeekDayCallback.filter(F.week_day == "Назад"))
async def back_to_week_type(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group_id = data.get('group')
    if not group_id:
        await call.message.answer("Данные отсутствуют. Пожалуйста, начните заново.")
        await state.clear()
        return
    await choose_way_to_navigate(call, state, group_id)


@ScheduleByTimeRouter.callback_query(ByTimeState.week_day, WeekDayCallback.filter())
async def send_day_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    await call.answer()
    data = await state.get_data()
    user_id = call.from_user.id
    # Используем get() с проверкой
    class_time = data.get('class_time')
    week_type = data.get('week_type')
    faculty_id = await send_request_mq('admin_bot.tasks.get_faculty_id', [user_id])

    #group_id = data.get('group')
    name_weekday = callback_data.week_day

    if not (class_time and week_type and faculty_id):
        await call.message.answer("Недостаточно данных для формирования расписания. Пожалуйста, начните заново.")
        await state.clear()
        return

    #group_number = await send_request_mq('admin_bot.tasks.get_group_number', [group_id])
    pares_for_groups_in_selected_time = await send_request_mq('bot.tasks.filter_groups_by_pare_time',
                                                              [faculty_id, class_time, name_weekday])

    # sorted_schedule_pare = await send_request_mq('bot.tasks.get_pare_for_group', [group_id, class_time, name_weekday])
    if pares_for_groups_in_selected_time:
        formatted_list = await format_groups_list(pares_for_groups_in_selected_time, week_type, name_weekday, class_time)
        if formatted_list:
            await call.message.answer(formatted_list, parse_mode=ParseMode.HTML)
        else:
            await call.message.answer(f"Расписание для групп на этот день и в это время не найдено")


    messages_data = (await state.get_data()).get("messages_to_delete", [])
    try:
        for message_id in messages_data:
            await call.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)
    await state.clear()
