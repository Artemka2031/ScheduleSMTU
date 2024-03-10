from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Bot.Keyboards.menu_kb import create_menu_kb, CanselMenuCallback
from Bot.Middlewares import IsRegMiddleware
from .SubRouters.week_router import WeekScheduleRouter
from Bot.Routers.MenuRouter.menu_state import MenuState

MenuRouter = Router()

MenuRouter.message.middleware(IsRegMiddleware())


@MenuRouter.message(Command("menu"))
@MenuRouter.message(F.text == "Главное меню")
async def send_menu(message: Message, state: FSMContext):
    await state.clear()
    sent_message = await message.answer(text="Вы в главном меню", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_message_id)
    await state.update_data(menu_message_id=sent_message.message_id)
    await state.set_state(MenuState.menu_option)

MenuRouter.include_router(WeekScheduleRouter)


@MenuRouter.callback_query(CanselMenuCallback.filter(F.cansel == True))
async def send_menu(call: Message, state: FSMContext):
    await state.clear()
    sent_message = await call.message.edit_text(text="Вы в главном меню", reply_markup=create_menu_kb())
    await state.set_state(MenuState.menu_message_id)
    await state.update_data(menu_message_id=sent_message.message_id)
    await state.set_state(MenuState.menu_option)
