from aiogram.fsm.state import StatesGroup, State


class AuthorizationBotStates(StatesGroup):
    choose_role = State()
    teacher_authorization = State()
