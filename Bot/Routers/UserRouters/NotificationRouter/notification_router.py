from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.markdown import hbold

from Bot.Keyboards.notification_inl_kb import notification_kb, NotificationCallback
from Bot.Middlewares.authentication_middleware import IsRegMiddleware
from Bot.RabbitMQProducer.producer_api import send_request_mq

from Bot.Keyboards.time_for_notification_inl_kb import NotificationTimeCallback, notification_time_kb

NotificationRouter = Router()

NotificationRouter.message.middleware(IsRegMiddleware())


class NotificationState(StatesGroup):
    user_id = State()
    time_to_send = State()
    apply_notification = State()
    message_from_user = State()


@NotificationRouter.message(Command("notification"))
async def notification_request(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.set_state(NotificationState.user_id)
    await message.answer(text="Вы хотите заранее получать расписание на текущий день?", reply_markup=notification_kb())

    await state.update_data(user_id=message.from_user.id)

    await state.set_state(NotificationState.message_from_user)
    await state.set_state(NotificationState.apply_notification)


@NotificationRouter.callback_query(NotificationState.apply_notification, NotificationCallback.filter())
async def choose_notification_time(call: CallbackQuery, state: FSMContext, callback_data: NotificationCallback) -> None:
    await call.message.bot.delete_messages(chat_id=call.message.chat.id, message_ids=[call.message.message_id])
    data = (await state.get_data())["user_id"]
    if callback_data.notification_apply == "Да":
        await call.message.answer("Выберите время, в которое вы хотите получать уведомления 🕘",
                                  reply_markup=notification_time_kb())
        await state.set_state(NotificationState.time_to_send)
    elif callback_data.notification_apply == "Нет":
        await state.clear()
        return
    else:

        has_subscription_flag = await send_request_mq('bot.tasks.has_subscription', [data])
        if has_subscription_flag:
            await send_request_mq('bot.tasks.cancel_notification', [data])
            #Notification.cancel_notification(data)
        await call.message.answer("Вы успешно отменили подписку на уведомления")
        await state.clear()
        return


@NotificationRouter.callback_query(NotificationState.time_to_send, NotificationTimeCallback.filter())
async def apply_notification_time(call: CallbackQuery, state: FSMContext,
                                  callback_data: NotificationTimeCallback) -> None:

    if callback_data.notification_time == 'cancel':
        await state.clear()
        await notification_request(call.message, state)
        return

    await state.update_data(time_to_send=callback_data.notification_time)

    data = await state.get_data()
    has_subscription_flag = await send_request_mq('bot.tasks.has_subscription', [data["user_id"]])
    if has_subscription_flag:
        await send_request_mq('bot.tasks.update_notification', [data["user_id"], data["time_to_send"]])
        #Notification.update_notification(data["user_id"], data["time_to_send"])
    elif not has_subscription_flag:
        await send_request_mq('bot.tasks.add_notification', [data["user_id"], data["time_to_send"]])
        #Notification.add_notification(data["user_id"], data["time_to_send"])

    await call.message.bot.delete_messages(chat_id=call.message.chat.id, message_ids=[call.message.message_id])
    await call.message.answer(f"Вы успешно установили время уведомлений на {hbold(data['time_to_send'] + ':00')}  🎉")
    await state.clear()
