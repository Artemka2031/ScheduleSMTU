from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Bot.Routers.UserRouters.StartRouter.registration import RegistrationState

StartRouter = Router()


@StartRouter.message(CommandStart())
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"Здравствуй студент Корабелки! Этот бот создан для того, чтобы ты мог не париться в поисках расписания.\n\n"
        f"Бот автоматически определяет текущую неделю и показывает актуальное расписание.\n\n"
        f"Если у вас есть пожелание и желание поддержать этого бота, то используйте команду /suggestion\n\n"
        f"Если вы хотите изменить группу, то используйте команду /change_group\n\n"
        f"Чтобы посмотреть расписание на любой день недели используйте команду /week_schedule\n\n"
        f"Все команды можно посмотреть в меню бота.",)

    sent_message = await message.answer(f"{hbold('Напиши номер совей группы и я смогу отправлять тебе расписание:')}")

    await state.set_state(RegistrationState.user_id)
    await state.update_data(user_id=message.from_user.id, messages_to_delete=[sent_message.message_id])
    await state.set_state(RegistrationState.group_number)
