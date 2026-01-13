from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from admin_bot.Filters.authentication_filter import isRegFilter
from admin_bot.Keyboards.faculties_inl_kb import add_faculty_kb, FacultyCallback
from admin_bot.Keyboards.main_reply_kb import main_menu_kb
from admin_bot.RabbitMQProducer.producer_api import send_request_mq

# from ORM.Tables.SceduleTables.group_tables import Faculty
# from ORM.Tables.UserTables.user_table import User

RegistrationRouter = Router()


class RegistrationState(StatesGroup):
    user_id = State()
    faculty = State()
    messages_to_delete = State()


@RegistrationRouter.message(Command("registration"), ~isRegFilter())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RegistrationState.user_id)

    sent_message = await message.answer(f"{hbold('Выберите интересующий вас факультет:')}",
                                        reply_markup=await add_faculty_kb(),
                                        parse_mode=ParseMode.HTML)

    await state.update_data(user_id=message.from_user.id,
                            messages_to_delete=[sent_message.message_id, message.message_id])
    await state.set_state(RegistrationState.faculty)


@RegistrationRouter.message(Command("registration"), isRegFilter())
async def already_registered(message: Message, state: FSMContext):
    await state.clear()
    users_faculty = await send_request_mq('admin_bot.tasks.get_faculty_name', [message.from_user.id])
    await message.answer(
        text=f"Вы уже зарегистрированы. Ваша текущий факультет: {hbold(users_faculty)}.\n\n"
             f"Чтобы изменить факультет, напишите /change_group или нажмите на соответствующую кнопку в меню.",
        reply_markup=main_menu_kb(),
        parse_mode=ParseMode.HTML
    )


@RegistrationRouter.callback_query(RegistrationState.faculty, FacultyCallback.filter())
async def set_faculty(call: CallbackQuery, state: FSMContext, callback_data: FacultyCallback):
    await call.answer()

    user_id = call.from_user.id
    faculty_id = callback_data.faculty_id
    faculty = await send_request_mq('admin_bot.tasks.get_faculty_name_by_id', [faculty_id])

    try:
        await send_request_mq('admin_bot.tasks.registrate_user', [user_id, faculty, faculty_id])
    except Exception as e:
        print(e)

    data = (await state.get_data())["messages_to_delete"]
    data.append(call.message.message_id)

    try:
        for message_id in data:
            await call.bot.delete_message(user_id, message_id)
    except Exception as e:
        print(e)

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение пользователю
    await call.message.answer(f"Выбран факультет {hbold(faculty)}.",
                              reply_markup=main_menu_kb(), parse_mode=ParseMode.HTML)
