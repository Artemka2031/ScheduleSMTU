from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import italic, hbold, hitalic
from aiogram_calendar import DialogCalendar, get_user_locale, DialogCalendarCallback

from admin_bot.Keyboards.classtime_inl_kb import classtime_kb, ClassTimeCallback
from admin_bot.Keyboards.week_schedule_inl_kb import week_type_kb, WeekTypeCallback, week_day_kb, WeekDayCallback
from admin_bot.Keyboards.list_buildings_inl_kb import buildings_list_kb, BuildingsListCallback
from admin_bot.Middlewares import IsRegMiddleware

from admin_bot.RabbitMQProducer.producer_api import send_request_mq


class AudienceState(StatesGroup):
    class_time = State()
    building = State()
    menu = State()
    week_type = State()
    week_day = State()
    calendar = State()
    set_month_calendar = State()

AudienceRouter = Router()
AudienceRouter.message.middleware(IsRegMiddleware())

@AudienceRouter.message(F.text == 'Фонд аудиторий')
async def audience_fond(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text=f'Выберите из списка время {italic("интересующей пары")}: ',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await classtime_kb()
    )

    await state.set_state(AudienceState.building)

@AudienceRouter.callback_query(AudienceState.building, ClassTimeCallback.filter(F.classtime_id == 'cancel'))
async def cancel_set_classtime(call: CallbackQuery, state: FSMContext, callback_data: ClassTimeCallback):
    await call.answer()
    try:
        await call.bot.delete_messages(chat_id=call.from_user.id, message_ids=[call.message.message_id, call.message.message_id-1])
    except Exception as e:
        print(e)

    await state.clear()

@AudienceRouter.callback_query(AudienceState.building, ClassTimeCallback.filter())
async def select_building(call: CallbackQuery, state: FSMContext, callback_data:ClassTimeCallback):
    await call.answer()
    if type(callback_data) == str:
        class_time_id = callback_data
    else:
        class_time_id = callback_data.classtime_id

    await state.update_data(class_time=class_time_id)

    class_time_text = await send_request_mq('bot.tasks.get_time_text_by_id', [class_time_id])

    await call.message.edit_text(
        text=f'Выбранное время: {hbold(str(class_time_text))}\nВыберите литеру:',
        reply_markup=buildings_list_kb(),
        parse_mode=ParseMode.HTML
    )

    await state.set_state(AudienceState.week_type)

@AudienceRouter.callback_query(AudienceState.week_type, BuildingsListCallback.filter(F.building=='cancel'))
async def cancel_select_building(call: CallbackQuery, state: FSMContext, callback_data:BuildingsListCallback):
    await call.answer()
    await state.clear()
    try:
        await call.bot.delete_messages(chat_id=call.from_user.id,message_ids=[call.message.message_id])
    except Exception as e:
        print(e)
    await audience_fond(call.message, state)

@AudienceRouter.callback_query(AudienceState.week_type, BuildingsListCallback.filter())
async def select_week_type(call: CallbackQuery, state: FSMContext, callback_data:BuildingsListCallback):
    await call.answer()

    if type(callback_data) == str:
        building = callback_data
    else:
        building = callback_data.building

    await state.update_data(building=building)

    await call.message.edit_text(
        text=f'👇 Выбери тип недели или воспользуйся виджетом календаря для выбора конкретной даты!',
        parse_mode=ParseMode.HTML,
        reply_markup=week_type_kb(back_to_menu=True)
    )


    await state.set_state(AudienceState.menu)

@AudienceRouter.callback_query(AudienceState.menu, WeekTypeCallback.filter(F.week_type=='Назад'))
async def cancel_select_weektype(call: CallbackQuery, state: FSMContext, callback_data:WeekTypeCallback):
    await call.answer()
    data = await state.get_data()
    class_time = data['class_time']
    await select_building(call, state, class_time)


@AudienceRouter.callback_query(AudienceState.menu, WeekTypeCallback.filter(F.week_type=='Открыть календарь'))
async def get_calendar(call: CallbackQuery, state: FSMContext, callback_data: WeekTypeCallback):

    await call.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(locale=await get_user_locale(call.from_user)).start_calendar(
            year=datetime.now().year, month=datetime.now().month)
    )

    data = (await state.get_data()).get("messages_to_delete", [])
    data.append(call.message.message_id)
    await state.update_data(messages_to_delete=data)

    await state.set_state(AudienceState.calendar)

@AudienceRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-YEAR"))
async def init_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                     state: FSMContext):
    current_state = await state.get_state()

    if current_state == AudienceState.calendar:
        await DialogCalendar(
            locale=await get_user_locale(callback_query.from_user)
        ).process_selection(callback_query, callback_data)
        print(callback_data)
        await state.set_state(AudienceState.set_month_calendar)

@AudienceRouter.callback_query(DialogCalendarCallback.filter(F.act == "SET-MONTH"), AudienceState.set_month_calendar)
async def process_dialog_calendar_month(callback_query: CallbackQuery, callback_data: DialogCalendarCallback,
                                        state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📅 Пожалуйста, выберите дату из календаря ниже:",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(callback_query.from_user)
        ).start_calendar(
            year=datetime.now().year,
            month=callback_data.month
        )
    )
    await state.set_state(AudienceState.calendar)

@AudienceRouter.callback_query(AudienceState.calendar, DialogCalendarCallback.filter(F.act == "SET-DAY"))
async def return_audience_list(call: CallbackQuery, state: FSMContext, callback_data: DialogCalendarCallback):
    selected, date = await DialogCalendar(
        locale=await get_user_locale(call.from_user)
    ).process_selection(call, callback_data)

    if selected:
        week_type = await send_request_mq('bot.tasks.determine_week_type', [str(date)])
        week_type_id = await send_request_mq('bot.tasks.get_week_type_id', [week_type])
        name_weekday = await send_request_mq('bot.tasks.get_weekday_name', [str(date)])
        week_day_id = await send_request_mq('bot.tasks.get_weekday_id', [name_weekday])

        data = await state.get_data()

        building = data['building']
        class_time = data['class_time']
        buildings_list = await send_request_mq('admin_bot.tasks.get_free_audience', [class_time, building, week_type_id, week_day_id])
        sorted_message = '📎 Список свободных аудиторий:\n\n'

        for building, room_number in buildings_list.items():
            for number in room_number:
                sorted_message += f'{hbold(building)} - {hitalic(number)}\n'

        await call.message.edit_text(
            text=sorted_message,
            parse_mode=ParseMode.HTML
        )

        await state.clear()

@AudienceRouter.callback_query(DialogCalendarCallback.filter(F.act == "CANCEL"))
async def back_to_menu_from_calendar(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    old_building = data['building']
    await select_week_type(callback_query, state, old_building)

@AudienceRouter.callback_query(AudienceState.menu, WeekTypeCallback.filter())
async def select_day(call: CallbackQuery, state: FSMContext, callback_data:WeekTypeCallback):
    await call.answer()

    chosen_wt = callback_data.week_type
    await call.message.edit_text(
        text=f"🔄 Выбранный тип недели: {hbold(chosen_wt)}.\n\n👉 Теперь выбери день недели:",
        reply_markup=week_day_kb(),
        parse_mode=ParseMode.HTML,
    )
    await state.update_data(week_type=chosen_wt)
    await state.set_state(AudienceState.week_day)

@AudienceRouter.callback_query(AudienceState.week_day, WeekDayCallback.filter(F.week_day=='Назад'))
async def cancel_select_day(call: CallbackQuery, state: FSMContext, callback_data: WeekDayCallback):
    await call.answer()
    data = await state.get_data()
    old_building = data['building']
    await select_week_type(call, state, old_building)

@AudienceRouter.callback_query(AudienceState.week_day, WeekDayCallback.filter())
async def output_info(call: CallbackQuery, state: FSMContext, callback_data:WeekDayCallback):
    week_day_name = callback_data.week_day
    week_day_id = await send_request_mq('bot.tasks.get_weekday_id', [week_day_name])
    data = await state.get_data()

    week_type = data['week_type']
    week_type_id = await send_request_mq('bot.tasks.get_week_type_id', [week_type])
    class_time = data['class_time']
    building = data['building']

    buildings_list = await send_request_mq('admin_bot.tasks.get_free_audience', [class_time, building, week_type_id, week_day_id])
    sorted_message = '📎 Список свободных аудиторий:\n\n'

    for building, room_number in buildings_list.items():
        for number in room_number:
            sorted_message += f'{hbold(building)} - {hitalic(number)}\n'

    await call.message.edit_text(
        text = sorted_message,
        parse_mode=ParseMode.HTML
    )

    await state.clear()
