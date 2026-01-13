from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram_calendar import DialogCalendar, get_user_locale, DialogCalendarCallback

from admin_bot.Keyboards.menu_kb import create_teachers_kb, TeacherCallback
from admin_bot.Keyboards.teacher_text_kb import create_choose_teachers_kb, TeacherTextCallback
from admin_bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from admin_bot.RabbitMQProducer.producer_api import send_request_mq
from admin_bot.Routers.UserRouters.menu_state import MenuState
from admin_bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_teacher_dual_week_schedule, \
    format_teacher_schedule
from admin_bot.bot_initialization import bot

TeacherRouter = Router()

class TeacherState(StatesGroup):
    teacher_text = State()
    teacher_callback = State()
    teacher_text_week_type = State()
    teacher_text_week_day = State()

@TeacherRouter.message(F.text == 'По преподавателю')
async def pick_teacher(message: Message, state: FSMContext):

    faculty_id = await send_request_mq('admin_bot.tasks.get_faculty_id', [message.from_user.id])

    teachers = await send_request_mq('admin_bot.tasks.get_teachers_for_faculty', [faculty_id])
    await message.answer('Введите фамилию преподавателя или выберите любого преподавателя из вашего факультета при помощи клавитуры снизу👨🏻‍🏫',
                         reply_markup=create_teachers_kb(teachers)
                         )

    await state.set_state(MenuState.teacher)

@TeacherRouter.callback_query(MenuState.teacher, TeacherCallback.filter() or TeacherTextCallback.filter())
async def send_choose_week_schedule(call: CallbackQuery, state: FSMContext, callback_data: TeacherCallback):
    await call.answer()
    await state.update_data(teacher=callback_data.teacher)

    teacher = await send_request_mq('bot.tasks.get_teacher', [callback_data.teacher])
    current_weektype = await send_request_mq('bot.tasks.get_current_week', [])


    await call.message.edit_text(
        text=f"📅 Текущий тип недели: {hbold(current_weektype)}\n\n"
             f"👨‍🏫 Выбранный преподаватель: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "🔄 Выберите тип недели:",
        reply_markup=week_type_kb(back_to_menu=True),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(MenuState.teacher_week_type)

@TeacherRouter.callback_query(MenuState.teacher_week_type, WeekTypeCallback.filter(F.week_type == "Назад"))
async def back_to_teachers(call: CallbackQuery, state: FSMContext):
    await call.answer()

    faculty_id = await send_request_mq('admin_bot.tasks.get_faculty_id', [call.from_user.id])

    teachers = await send_request_mq('admin_bot.tasks.get_teachers_for_faculty', [faculty_id])

    await call.message.edit_text(
        'Введите фамилию преподавателя или выберите любого преподавателя из вашего факультета при помощи клавитуры снизу👨🏻‍🏫',
        reply_markup=create_teachers_kb(teachers)
        )

    await state.set_state(MenuState.teacher)

@TeacherRouter.callback_query(WeekTypeCallback.filter(F.week_type == "Открыть календарь"),
                              StateFilter(MenuState.teacher_week_type, TeacherState.teacher_text_week_type)
)
async def get_teachers_calendar(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(locale=await get_user_locale(call.from_user)).start_calendar(
            year=datetime.now().year, month=datetime.now().month)
    )
    await state.set_state(MenuState.teacher_calendar)


@TeacherRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-YEAR"))
async def init_dialog_calendar_teacher_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                             state: FSMContext):
    await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    await state.set_state(MenuState.set_month_teacher)


@TeacherRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-MONTH"), MenuState.set_month_teacher)
async def process_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                        state: FSMContext):
    await callback_query.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(locale=await get_user_locale(callback_query.from_user)).start_calendar(
            year=datetime.now().year, month=callback_data.month)
    )
    await state.set_state(MenuState.teacher_calendar)


@TeacherRouter.callback_query(MenuState.teacher_calendar, DialogCalendarCallback.filter(F.act == "SET-DAY"))
async def process_dialog_teacher_calendar(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                          state: FSMContext):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:

        determine_weektype = await send_request_mq('bot.tasks.determine_week_type', [str(date)])
        await state.update_data(teacher_week_type=determine_weektype)

        data = await state.get_data()

        teacher_id = data.get('teacher') or data.get('teacher_text')
        teacher_week_type = data['teacher_week_type']

        teacher = await send_request_mq('bot.tasks.get_teacher', [teacher_id])

        name_weekday = await send_request_mq('bot.tasks.get_weekday_name', [str(date)])

        sorted_schedule = await send_request_mq('bot.tasks.get_schedule_teacher', [teacher_id, name_weekday])

        if sorted_schedule and any(sorted_schedule.values()):
            schedule = format_teacher_schedule(sorted_schedule, teacher_week_type)
            await callback_query.message.edit_text(
                text=f"📚 Расписание для преподавателя: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}:\n\n{schedule}",
                parse_mode=ParseMode.HTML
            )
        else:
            await callback_query.message.edit_text(
                text = f"😅 Извините, у преподавателя {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])} нет пар в этот день.",
                parse_mode=ParseMode.HTML
            )
    await state.clear()

    await state.update_data(menu_message_id=callback_query.message.message_id)
    await state.set_state(MenuState.menu_option)


@TeacherRouter.callback_query(MenuState.teacher_week_type, WeekTypeCallback.filter())
async def send_choose_day_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    await call.message.edit_text(
        text=f"🔄 Выбранный тип недели: {hbold(callback_data.week_type)}.\n\n👉 Теперь выбери день недели:",
        reply_markup=week_day_kb(),
        parse_mode=ParseMode.HTML)
    await state.update_data(teacher_week_type=callback_data.week_type)
    await state.set_state(MenuState.teacher_week_day)


@TeacherRouter.callback_query(MenuState.teacher_week_day, WeekDayCallback.filter(F.week_day == "Назад"))
async def back_to_week_type(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await state.update_data(teacher_week_type=None)
    teacher = (await state.get_data())['teacher']

    teacher = await send_request_mq('bot.tasks.get_teacher', [teacher])

    current_week = await send_request_mq('bot.tasks.get_current_week', [])

    await call.message.edit_text(
        text=f"📅 Текущий тип недели: {hbold(current_week)}\n\n"
             f"👨‍🏫 Выбранный преподаватель: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "🔄 Выберите тип недели:",
        reply_markup=week_type_kb(back_to_menu=True),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(MenuState.teacher_week_type)


@TeacherRouter.callback_query(MenuState.teacher_week_day, WeekDayCallback.filter())
async def send_teacher_info(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    data = await state.get_data()
    teacher_id = data['teacher']
    week_type = data["teacher_week_type"]


    teacher = await send_request_mq('bot.tasks.get_teacher', [teacher_id])

    sorted_schedule = await send_request_mq('bot.tasks.get_schedule_teacher', [teacher_id, callback_data.week_day])

    # Проверяем, что расписание существует и содержит занятия
    if sorted_schedule and any(sorted_schedule.values()):
        if week_type == "Обе недели":
            schedule = format_teacher_dual_week_schedule(sorted_schedule)
        else:
            schedule = format_teacher_schedule(sorted_schedule, week_type)

        await call.message.edit_text(
            text=f"📚 Расписание для преподавателя: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}:\n\n{schedule}",
            parse_mode=ParseMode.HTML
        )
    else:
        # Если у преподавателя нет пар
        await call.message.edit_text(
            text = f"😅 Извините, у преподавателя {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])} нет пар в этот день.",
            parse_mode=ParseMode.HTML
        )

    await state.clear()
    await state.update_data(menu_message_id=call.message.message_id)
    await state.set_state(MenuState.menu_option)


@TeacherRouter.message(MenuState.teacher)
async def get_teachers(message: Message, state: FSMContext):
    teacher_last_name = message.text.strip().replace('ё', 'е')

    await state.set_state(TeacherState.teacher_text)

    try:
        await bot.delete_messages(message.from_user.id, [message.message_id, message.message_id-1])

        teachers = await send_request_mq('bot.tasks.get_teacher_by_last_name', [teacher_last_name])
        #teachers = Teacher.get_teacher_by_last_name(teacher_last_name)

        current_week = await send_request_mq('bot.tasks.get_current_week', [])

        if len(teachers) == 1:
            teacher = teachers[0]
            await state.update_data(teacher_text=teacher["id"])

            await message.answer(
                text=f"📅 Текущий тип недели: {hbold(current_week)}.\n\n"
                     f"👨‍🏫 Выбранный преподаватель: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
                     "🔄 Выберите тип недели:"
                ,
                reply_markup=week_type_kb(back_to_menu=True),
                parse_mode=ParseMode.HTML
            )

            await state.set_state(TeacherState.teacher_text_week_type)
        elif len(teachers) > 1:
            await message.answer(
                text=f"👨‍🏫 Список преподавателей с фамилией '{hbold(teacher_last_name)}':",
                reply_markup=create_choose_teachers_kb(teachers),
                parse_mode=ParseMode.HTML)
            await state.set_state(TeacherState.teacher_text)
        else:
            await message.answer("😕 Преподаватели с такой фамилией не найдены. Пожалуйста, введи фамилию ещё раз:")
            await state.set_state(MenuState.teacher)
    except ValueError as e:
        await message.answer(text=str(e) + " Введите фамилию еще раз:")
        await state.set_state(MenuState.teacher)


@TeacherRouter.callback_query(TeacherState.teacher_text, TeacherTextCallback.filter())
async def set_teacher(call: CallbackQuery, callback_data: TeacherTextCallback, state: FSMContext):

    teacher_id = callback_data.teacher
    await state.update_data(teacher_text=teacher_id)

    teacher = await send_request_mq('bot.tasks.get_teacher', [teacher_id])

    current_week = await send_request_mq('bot.tasks.get_current_week', [])

    menu_message_id = (await state.get_data())["menu_message_id"]

    await call.message.edit_text(
        text=f"📅 Текущий тип недели: {hbold(current_week)}.\n\n"
             f"👨‍🏫 Выбранный преподаватель: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "🔄 Выберите тип недели:",
        reply_markup=week_type_kb(back_to_menu=True),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(TeacherState.teacher_text_week_type)


@TeacherRouter.callback_query(TeacherState.teacher_text_week_type, WeekTypeCallback.filter(F.week_type == "Назад"))
async def back_to_teacher_choose(call: CallbackQuery, state: FSMContext):
    await call.answer()

    group_number = await send_request_mq('bot.tasks.get_group_number', [call.from_user.id])

    teachers = await send_request_mq('bot.tasks.get_teachers_for_group', [group_number])

    #teachers = GroupSchedule.get_teachers_for_group(BaseUser.get_group_number(call.from_user.id))
    await call.message.edit_text(text="👩‍🏫 Выбери преподавателя из списка или напиши его фамилию в чат:",
                                 reply_markup=create_teachers_kb(teachers))
    await state.set_state(MenuState.teacher)


@TeacherRouter.callback_query(TeacherState.teacher_text_week_type, WeekTypeCallback.filter())
async def send_choose_day_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    await call.message.edit_text(
        text=f"🔄 Выбранный тип недели: {hbold(callback_data.week_type)}.\n\n👉 Теперь выбери день недели:",
        reply_markup=week_day_kb(),
        parse_mode=ParseMode.HTML)
    await state.update_data(teacher_text_week_type=callback_data.week_type)
    await state.set_state(TeacherState.teacher_text_week_day)


@TeacherRouter.callback_query(TeacherState.teacher_text_week_day, WeekDayCallback.filter(F.week_day == "Назад"))
async def back_to_week_type(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await state.update_data(teacher_text_week_type=None)
    teacher = (await state.get_data())['teacher_text']

    current_week = await send_request_mq('bot.tasks.get_current_week', [])

    await call.message.edit_text(
        text=f"📅 Текущий тип недели: {hbold(current_week)}.\n\n"
             f"👨‍🏫 Выбранный преподаватель: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "🔄 Выберите тип недели:"
        ,
        reply_markup=week_type_kb(back_to_menu=True),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TeacherState.teacher_text_week_type)


@TeacherRouter.callback_query(TeacherState.teacher_text_week_day, WeekDayCallback.filter())
async def send_teacher_info(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    data = await state.get_data()
    teacher_id = data['teacher_text']
    week_type = data["teacher_text_week_type"]

    teacher = await send_request_mq('bot.tasks.get_teacher', [teacher_id])
    #teacher = Teacher.get_teacher(teacher_id)

    sorted_schedule = await send_request_mq('bot.tasks.get_schedule_teacher', [teacher_id, callback_data.week_day])
    #sorted_schedule = GroupSchedule.get_schedule_teacher(teacher_id, callback_data.week_day)

    # Проверяем, что расписание существует и содержит занятия
    if sorted_schedule and any(sorted_schedule.values()):
        if week_type == "Обе недели":
            schedule = format_teacher_dual_week_schedule(sorted_schedule)
        else:
            schedule = format_teacher_schedule(sorted_schedule, week_type)

        await call.message.edit_text(
            text=f"📚 Расписание для преподавателя: {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}:\n\n{schedule}",
            parse_mode=ParseMode.HTML
        )
    else:
        # Если у преподавателя нет пар
        await call.message.edit_text(
            text=f"😅 Извините, у преподавателя {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])} нет пар в этот день.",
            parse_mode=ParseMode.HTML
        )

    await state.clear()
    await state.update_data(menu_message_id=call.message.message_id)
    await state.set_state(MenuState.menu_option)
