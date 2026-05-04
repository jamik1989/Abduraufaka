from aiogram.fsm.state import State, StatesGroup


class LoginStates(StatesGroup):
    waiting_phone = State()
    waiting_password = State()


class AdminStates(StatesGroup):
    waiting_agent_name = State()
    waiting_agent_phone = State()
    waiting_agent_password = State()


class VisitStates(StatesGroup):
    waiting_address = State()
    waiting_landmark = State()
    waiting_client_code = State()
    waiting_last_visit_date = State()
    waiting_stand_code = State()
    waiting_client_comment = State()
    waiting_conclusion = State()
    waiting_stand_photo = State()
    waiting_product_photo = State()
    waiting_outside_photo = State()
    confirm = State()
