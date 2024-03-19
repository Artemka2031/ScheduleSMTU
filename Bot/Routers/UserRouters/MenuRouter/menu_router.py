from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.Keyboards.menu_kb import create_menu_kb, CanselMenuCallback, TeacherCallback
from Bot.Middlewares import IsRegMiddleware
from Bot.Routers.UserRouters.MenuRouter.menu_state import MenuState
from .SubRouters import WeekScheduleRouter, TeacherRouter
from Bot.Keyboards.teacher_text_kb import TeacherTextCallback

MenuRouter = Router()

MenuRouter.message.middleware(IsRegMiddleware())


@MenuRouter.message(Command("/schedule"))
@MenuRouter.message(F.text == "Расписание")
async def send_menu(message: Message, state: FSMContext):
    await state.clear()
    sent_message = await message.answer(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_message_id)
    await state.update_data(menu_message_id=sent_message.message_id)
    await state.set_state(MenuState.menu_option)


MenuRouter.include_router(WeekScheduleRouter)
MenuRouter.include_router(TeacherRouter)


@MenuRouter.callback_query(CanselMenuCallback.filter(F.cansel == True))
@MenuRouter.callback_query(
    TeacherCallback.filter(F.teacher == "Назад") or TeacherTextCallback.filter(F.teacher == "Назад"))
async def send_menu(call: Message, state: FSMContext):
    await state.clear()
    sent_message = await call.message.edit_text(text="Вы находитесь в меню расписания!", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_message_id)
    await state.update_data(menu_message_id=sent_message.message_id)
    await state.set_state(MenuState.menu_option)
