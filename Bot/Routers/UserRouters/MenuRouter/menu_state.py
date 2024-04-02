from aiogram.fsm.state import StatesGroup, State


class MenuState(StatesGroup):
    menu_message_id = State()
    menu_option = State()

    week_type = State()
    week_day = State()

    teacher = State()
    teacher_week_type = State()
    teacher_week_day = State()

    teacher_calendar = State()
    group_calendar = State()

    set_month_teacher = State()
    set_month_group = State()
