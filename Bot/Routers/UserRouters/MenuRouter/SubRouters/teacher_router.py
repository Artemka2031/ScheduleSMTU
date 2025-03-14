from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.menu_kb import TeacherCallback, create_menu_kb, create_teachers_kb, MenuCallback
from Bot.RabbitMQProducer.producer_api import send_request_mq
from Bot.Routers.UserRouters.MenuRouter.SubRouters.TeachersRouters import TeacherRouterCallback, TeacherRouterText
from Bot.Routers.UserRouters.MenuRouter.menu_state import MenuState

TeacherRouter = Router()

@TeacherRouter.callback_query(MenuState.menu_option, MenuCallback.filter(F.operation == "teachers"))
async def send_teachers(call: CallbackQuery, state: FSMContext):
    await call.answer()

    group_number = await send_request_mq('bot.tasks.get_group_number', [call.from_user.id])

    teachers = await send_request_mq('bot.tasks.get_teachers_for_group', [group_number])
    #teachers = GroupSchedule.get_teachers_for_group(BaseUser.get_group_number(call.from_user.id))

    await call.message.edit_text(text="👩‍🏫👨‍🏫 Выбери преподавателя из списка или просто напиши его фамилию в чат!",
                                 reply_markup=create_teachers_kb(teachers))

    await state.set_state(MenuState.teacher)


@TeacherRouter.callback_query(MenuState.teacher, TeacherCallback.filter(F.teacher_text == "Назад"))
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(text="📚 Ты в меню расписания! Выбирай, что хочешь посмотреть! 😉", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_option)


TeacherRouter.include_router(TeacherRouterCallback)
TeacherRouter.include_router(TeacherRouterText)

