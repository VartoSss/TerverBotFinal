from aiogram.fsm.state import StatesGroup, State


class StudentBotStates(StatesGroup):
    start_state = State()
    default_state = State()
    upload_state_homework = State()
    upload_python_file = State()
