from aiogram.fsm.state import StatesGroup, State


class TeacherBotStates(StatesGroup):
    start_state = State()
    choosing_group = State()
    forming_group = State()
    default_state = State()
    picking_practice = State()
    picking_student = State()
    uploading_state = State()
    evaluating = State()
    commenting = State()
    evaluation_question = State()
    picking_group = State()
    deadline_not_found = State()
    choosing_deadline = State()
    downloading_state = State()
