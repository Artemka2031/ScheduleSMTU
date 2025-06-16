import asyncio

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from admin_bot.Filters.check_faculty_id_filter import CheckCurrentFacultyFilter
from admin_bot.Keyboards.change_current_faculty_kb import create_change_current_faculty_kb, ChangeCurrentFacultyCallback
from admin_bot.Keyboards.faculties_inl_kb import add_faculty_kb, FacultyCallback
from admin_bot.Keyboards.main_reply_kb import main_menu_kb
from admin_bot.RabbitMQProducer.producer_api import send_request_mq, update_cache

ChangeFacultyRouter = Router()

#ChangeFacultyRouter.message.middleware(IsRegMiddleware())

class ChangeFacultyState(StatesGroup):
    user_id = State()
    faculty = State()
    messages_to_delete = State()


@ChangeFacultyRouter.message(Command("change_faculty"))
async def change_faculty(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(messages_to_delete=[])

    await state.set_state(ChangeFacultyState.user_id)
    users_faculty = await send_request_mq('admin_bot.tasks.get_faculty_name', [message.from_user.id])
    sent_message = await message.answer(
        f"Ваш текущий факультет {hbold(users_faculty)}.\nОставьте текущий или выберите другой:",
        parse_mode=ParseMode.HTML,
        reply_markup=create_change_current_faculty_kb()
    )

    await state.update_data(messages_to_delete=[message.message_id, sent_message.message_id])


@ChangeFacultyRouter.callback_query(ChangeCurrentFacultyCallback.filter(F.change_faculty_flag == False))
async def cancel_change_faculty(query: Message, state: FSMContext):
    user_id = query.from_user.id

    data = (await state.get_data())["messages_to_delete"]
    data.append(query.message.message_id)

    try:
        for message_id in data:
            await query.message.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    users_faculty = await send_request_mq('admin_bot.tasks.get_faculty_name', [query.from_user.id])
    await query.message.answer(f"Выбран {hbold(users_faculty)}",
                               parse_mode=ParseMode.HTML,
                               reply_markup=main_menu_kb())
    await state.clear()


@ChangeFacultyRouter.callback_query(ChangeCurrentFacultyCallback.filter((F.change_faculty_flag == True)))
async def set_faculty(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.answer(text='Выберите интересующий вас факультет', reply_markup=await add_faculty_kb())

    await state.set_state(ChangeFacultyState.faculty)


@ChangeFacultyRouter.callback_query(ChangeFacultyState.faculty, FacultyCallback.filter(), CheckCurrentFacultyFilter())
async def change_user_faculty(call: CallbackQuery, state: FSMContext, callback_data: FacultyCallback):
    await call.answer()

    user_id = call.from_user.id
    faculty_id = callback_data.faculty_id
    faculty = await send_request_mq('admin_bot.tasks.get_faculty_name_by_id', [faculty_id])

    await send_request_mq('admin_bot.tasks.change_faculty', [user_id, faculty])
    await update_cache(user_id)

    data = (await state.get_data())["messages_to_delete"]
    data.append(call.message.message_id)
    try:
        for message_id in data:
            await call.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    await call.message.answer(f"Выбран {hbold(faculty)}",
                              parse_mode=ParseMode.HTML,
                              reply_markup=main_menu_kb())
    # Сбрасываем состояние
    await state.clear()



@ChangeFacultyRouter.callback_query(ChangeFacultyState.faculty, FacultyCallback.filter(), ~CheckCurrentFacultyFilter())
async def same_faculty(call: CallbackQuery, state: FSMContext, callback_data: FacultyCallback):
    await call.answer()

    user_id = call.from_user.id
    data = (await state.get_data()).get("messages_to_delete", [])
    data.append(call.message.message_id)
    users_faculty = await send_request_mq('admin_bot.tasks.get_faculty_name', [user_id])
    sent_message = await call.message.answer(
        text=f"Факультет {hbold(users_faculty)} уже выбран.\nОставьте текущий или выберите новый:",
        parse_mode=ParseMode.HTML,
        reply_markup=create_change_current_faculty_kb())

    try:
        for message_id in data:
            await call.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)


    await state.update_data(messages_to_delete=[sent_message.message_id])

