from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import EditMessageText
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from Bot.Keyboards.menu_kb import create_teachers_kb, create_menu_kb
from Bot.Keyboards.teacher_text_kb import create_choose_teachers_kb, TeacherTextCallback
from Bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from Bot.Routers.UserRouters.MenuRouter.menu_state import MenuState
from Bot.Routers.UserRouters.ScheduleRouter.ScheduleRouters.format_functions import format_teacher_dual_week_schedule, \
    format_teacher_schedule
from Bot.bot_initialization import bot
from ORM.Tables.SceduleTables.group_schedule import GroupSchedule
from ORM.Tables.SceduleTables.group_tables import Teacher
from ORM.Tables.SceduleTables.time_tables import WeekType
from ORM.Tables.UserTables.user_table import User

TeacherRouterText = Router()


class TeacherState(StatesGroup):
    teacher_text = State()
    teacher_text_week_type = State()
    teacher_text_week_day = State()


@TeacherRouterText.message(MenuState.teacher)
async def get_teachers(message: Message, state: FSMContext):
    teacher_last_name = message.text.strip().replace('ё', 'е')
    chat_id = message.chat.id
    menu_message_id = (await state.get_data())["menu_message_id"]
    await message.delete()

    await state.set_state(TeacherState.teacher_text)

    try:
        teachers = Teacher.get_teacher_by_last_name(teacher_last_name)
        if len(teachers) == 1:
            teacher = teachers[0]
            await state.update_data(teacher_text=teacher["id"])

            await bot(EditMessageText(
                chat_id=chat_id, message_id=menu_message_id,
                text=f"Текущий тип недели: {hbold(WeekType.get_current_week())}.\n\n"
                     f"Выбранный преподаватель: "
                     f"{hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
                     "Выберите тип недели:",
                reply_markup=week_type_kb(back_to_menu=True)
            ))

            await state.set_state(MenuState.teacher_week_type)
        elif len(teachers) > 1:
            await bot(EditMessageText(chat_id=chat_id, message_id=menu_message_id,
                                      text=f"Список преподавателей с фамилией '{hbold(teacher_last_name)}': ",
                                      reply_markup=create_choose_teachers_kb(teachers)))
            await state.set_state(TeacherState.teacher_text)
        else:
            await message.answer("Преподаватели с такой фамилией не найдены. Введите фамилию еще раз:")
            await state.set_state(MenuState.teacher)
    except ValueError as e:
        await message.answer(text=str(e) + " Введите фамилию еще раз:")
        await state.set_state(MenuState.teacher)


@TeacherRouterText.callback_query(TeacherState.teacher_text, TeacherTextCallback.filter(F.teacher_text == "Назад"))
async def back_to_teacher_choose(call: CallbackQuery, state: FSMContext):
    await call.answer()
    teachers = GroupSchedule.get_teachers_for_group(User.get_group_number(call.from_user.id))
    await call.message.edit_text(text="Выберите преподавателя или напишите его фамилию",
                                 reply_markup=create_teachers_kb(teachers))
    await state.set_state(MenuState.teacher)


@TeacherRouterText.callback_query(TeacherState.teacher_text, TeacherTextCallback.filter())
async def set_teacher(call: CallbackQuery, callback_data: TeacherTextCallback, state: FSMContext):
    chat_id = call.message.chat.id

    teacher_id = callback_data.teacher
    await state.update_data(teacher_text=teacher_id)

    teacher = Teacher.get_teacher(teacher_id)

    menu_message_id = (await state.get_data())["menu_message_id"]

    await bot(EditMessageText(
        chat_id=chat_id, message_id=menu_message_id,
        text=f"Текущий тип недели: {hbold(WeekType.get_current_week())}.\n\n"
             f"Выбранный преподаватель: "
             f"{hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "Выберите тип недели:",
        reply_markup=week_type_kb(back_to_menu=True)
    ))

    await state.set_state(TeacherState.teacher_text_week_type)


@TeacherRouterText.callback_query(TeacherState.teacher_text_week_type, WeekTypeCallback.filter(F.week_type == "Назад"))
async def back_to_teacher_choose(call: CallbackQuery, state: FSMContext):
    await call.answer()
    teachers = GroupSchedule.get_teachers_for_group(User.get_group_number(call.from_user.id))
    await call.message.edit_text(text="Выберите преподавателя или напишите его фамилию",
                                 reply_markup=create_teachers_kb(teachers))
    await state.set_state(MenuState.teacher)


@TeacherRouterText.callback_query(TeacherState.teacher_text_week_type, WeekTypeCallback.filter())
async def send_choose_day_schedule(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):
    await call.answer()
    await call.message.edit_text(
        text=f"Выбранный тип недели: {hbold(callback_data.week_type)}.\n\nВыберите день недели:",
        reply_markup=week_day_kb())
    await state.update_data(teacher_text_week_type=callback_data.week_type)
    await state.set_state(TeacherState.teacher_text_week_day)


@TeacherRouterText.callback_query(TeacherState.teacher_text_week_day, WeekDayCallback.filter(F.week_day == "Назад"))
async def back_to_week_type(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await state.update_data(teacher_text_week_type=None)
    teacher = (await state.get_data())['teacher_text']

    await call.message.edit_text(
        text=f"Текущий тип недели: {hbold(WeekType.get_current_week())}.\n\n"
             f"Выбранный преподаватель: "
             f"{hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}\n\n"
             "Выберите тип недели:",
        reply_markup=week_type_kb(back_to_menu=True)
    )
    await state.set_state(TeacherState.teacher_text_week_type)


@TeacherRouterText.callback_query(TeacherState.teacher_text_week_day, WeekDayCallback.filter())
async def send_teacher_info(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    data = await state.get_data()
    teacher_id = data['teacher_text']
    week_type = data["teacher_text_week_type"]

    teacher = Teacher.get_teacher(teacher_id)

    sorted_schedule = GroupSchedule.get_schedule_teacher(teacher_id, callback_data.week_day)

    # Проверяем, что расписание существует и содержит занятия
    if sorted_schedule and any(sorted_schedule.values()):
        if week_type == "Обе недели":
            schedule = format_teacher_dual_week_schedule(sorted_schedule)
        else:
            schedule = format_teacher_schedule(sorted_schedule, week_type)

        await bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Расписание для преподавателя: "
                 f"{hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])}:\n\n{schedule}"
        )
    else:
        # Если у преподавателя нет пар
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Извините, у преподавателя {hbold(teacher['last_name'])} {hbold(teacher['first_name'])} {hbold(teacher['middle_name'])} нет пар в этот день."
        )

    await state.clear()

    await call.message.edit_text(
        text="Вы находитесь в меню расписания!",
        reply_markup=create_menu_kb()
    )
    await state.update_data(menu_message_id=call.message.message_id)
    await state.set_state(MenuState.menu_option)
