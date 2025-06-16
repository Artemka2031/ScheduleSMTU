from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from admin_bot.Keyboards.faculties_inl_kb import add_faculty_kb
from admin_bot.Routers.UserRouters.StartRouter.registration import RegistrationState

StartRouter = Router()


@StartRouter.message(CommandStart())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Здравствуйте! 👋\n\n"
        "Этот бот создан, чтобы упростить взаимодействие с учебным процессом и помочь вам оперативно управлять расписанием и другой административной информацией.\n\n"
        "👉 Просматривайте актуальное расписание занятий на любую неделю или конкретный день 📅 через удобный календарный виджет.\n\n"
        "👨‍🏫👩‍🏫 Нужно расписание преподавателей или студентов? Просто выберите нужную опцию в разделе 'Расписание' или введите имя преподавателя/группы, и бот предоставит вам полную информацию. 🔍\n\n"
        "🔄 Меняйте группы, просматривайте разные курсы и кафедры — бот сделает управление расписанием быстрым и удобным.\n\n"
        "💬 Есть предложения по улучшению работы бота или другие идеи? Сообщите нам через команду /suggestion — мы всегда открыты для ваших предложений!\n\n"
        "🔔 Хотите получать уведомления о важных изменениях в расписании или других событиях? Включите уведомления с помощью команды /notification.\n\n"
        "Мы стремимся сделать ваше взаимодействие с учебным процессом максимально удобным и эффективным. Используйте возможности бота для быстрого доступа к необходимой информации и оптимизации рабочего времени!"
    )

    sent_message = await message.answer(f"{hbold('Выберите интересующий вас факультет:')}", reply_markup=await add_faculty_kb(), parse_mode=ParseMode.HTML)

    await state.set_state(RegistrationState.user_id)
    await state.update_data(user_id=message.from_user.id, messages_to_delete=[sent_message.message_id])
    await state.set_state(RegistrationState.faculty)
