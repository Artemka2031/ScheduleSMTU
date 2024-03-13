from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.menu_kb import TeacherCallback, create_menu_kb, create_teachers_kb, MenuCallback
from Bot.Routers.MenuRouter.SubRouters.TeachersRouters import TeacherRouterCallback, TeacherRouterText
from Bot.Routers.MenuRouter.menu_state import MenuState
from ORM.Tables.SceduleTables.group_schedule import GroupSchedule
from ORM.Tables.UserTables.user_table import User

TeacherRouter = Router()


@TeacherRouter.callback_query(MenuState.menu_option, MenuCallback.filter(F.operation == "teachers"))
async def send_teachers(call: CallbackQuery, state: FSMContext):
    await call.answer()
    teachers = GroupSchedule.get_teachers_for_group(User.get_group_number(call.from_user.id))

    await call.message.edit_text(text="Выберите преподавателя или напишите его фамилию",
                                 reply_markup=create_teachers_kb(teachers))

    await state.set_state(MenuState.teacher)


@TeacherRouter.callback_query(MenuState.teacher, TeacherCallback.filter(F.teacher_text == "Назад"))
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_option)


TeacherRouter.include_router(TeacherRouterCallback)
TeacherRouter.include_router(TeacherRouterText)

