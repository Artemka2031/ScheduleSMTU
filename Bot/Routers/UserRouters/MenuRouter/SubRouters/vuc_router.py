from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from Bot.Keyboards.menu_kb import MenuCallback
from Bot.Routers.UserRouters.MenuRouter.menu_state import MenuState

VucRouter = Router()


@VucRouter.callback_query(MenuState.menu_option, MenuCallback.filter(F.operation == "vuc"))
async def send_vuc_schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    with open("ORM/VUC/NewSchedule/new_file_ids.txt", "r") as file:
        photo_id = file.readlines()[0].strip("\n")
    if not photo_id:
        await call.message.answer("Администратор пока еще не выложил расписание для ВУЦ 😔")
        return
    else:
        await call.message.answer_photo(photo=photo_id, caption="Расписание ВУЦ на эту неделю")

    await state.clear()




