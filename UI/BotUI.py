from aiogram import Bot, Dispatcher, F, types
from domain.domain_objects.TeacherDomain import TeacherDomain
from domain.domain_objects.StudentDomain import StudentDomain
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from UI.states.AuthorizationBotStates import AuthorizationBotStates
from UI.keyboards.AuthorizationDefaultKeyboard import AuthorizationDefaultKeyboard
from UI.keyboards.TeacherDefaultKeyboard import TeacherDefaultKeyboard
from UI.keyboards.TeacherPracticeNumbersKeyboard import TeacherPracticeNumbersKeyboard
from UI.keyboards.StudentCancelKeyboard import StudentCancelKeyboard
from UI.keyboards.TeacherGroupKeyboard import TeacherGroupKeyboard
from Enums.HomeworkTypes import HomeworkTypes
from Enums.EvaluationMode import EvaluationMode
from UI.states.TeacherBotStates import TeacherBotStates
from UI.keyboards.TeachersStudentsInlineKeyboard import TeachersStudentInlineKeyboard
from UI.states.StudentBotStates import StudentBotStates
from UI.keyboards.StudentDefaultKeyboard import StudentDefaultKeyboard
from UI.keyboards.StudentPythonFileKeyboard import StudentPythonFileKeyboard
from UI.keyboards.TeacherContinueEvaluationKeyboard import TeacherContinueEvaluationKeyboard
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
import os
import re
from dotenv import dotenv_values


class BotUI:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    teacher_domain = TeacherDomain()
    student_domain = StudentDomain()
    scheduler = AsyncIOScheduler()
    bot = Bot(token=dotenv_values(".env")["BOT_TOKEN"])

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        BotUI.teacher_domain.create_database()

    async def run(self):
        await BotUI.bot.delete_webhook(drop_pending_updates=True)
        self.scheduler.start()
        await BotUI.dp.start_polling(BotUI.bot)

    # Авторизация --------------------------------------------------
    @staticmethod
    @dp.message(Command("start"))
    async def start_handler_teacher(message: types.Message, state: FSMContext):
        await message.answer("Привет! Для начала нужно пройти небольшую авторизацию, кто ты?",
                             reply_markup=AuthorizationDefaultKeyboard.get_keyboard())
        await state.set_state(AuthorizationBotStates.choose_role)

    #--------------------------------------------------------------
    #------------------ Учитель -----------------------------------
    @staticmethod
    @dp.message(
        AuthorizationBotStates.choose_role,
        F.text == "Я преподаватель"
    )
    async def authorize_teacher(message: types.Message, state: FSMContext):
        await message.answer("Введите код подтверждения", reply_markup=ReplyKeyboardRemove())
        await state.set_state(AuthorizationBotStates.teacher_authorization)

    @staticmethod
    @dp.message(
        AuthorizationBotStates.teacher_authorization,
        F.text == dotenv_values(".env")['TEACHER_CODE']
    )
    async def approve_teacher(message: types.Message, state: FSMContext):
        if not BotUI.teacher_domain.is_students_database_filled():
            await message.answer(
                "Отлично! Для начала нужно создать списки групп. Отправьте файл .csv с списком групп",
                reply_markup=ReplyKeyboardRemove())
            await state.set_state(TeacherBotStates.forming_group)
        elif not BotUI.teacher_domain.is_homework_info_database_filled():
            await message.answer(text="Теперь нужно установить дедлайн для первой домашки:")
            await message.answer(text="Пришлите дату и время дедлайна в формате:\ndd.mm hh:mm")
            await state.set_state(TeacherBotStates.choosing_deadline)
        else:
            await message.answer("Вы успешно зарегистрировались как преподаватель",
                                 reply_markup=TeacherDefaultKeyboard.get_keyboard())
            await BotUI.update_scheduler_on_last_deadline()
            await state.set_state(TeacherBotStates.default_state)

    @staticmethod
    @dp.message(
        AuthorizationBotStates.teacher_authorization
    )
    async def reject_teacher(message: types.Message, state: FSMContext):
        await message.answer("Это неверный код",
                             reply_markup=AuthorizationDefaultKeyboard.get_keyboard())
        await state.set_state(AuthorizationBotStates.choose_role)

    # ------------------ Формировка групп --------------------------
    @staticmethod
    @dp.message(
        TeacherBotStates.forming_group,
        F.document.file_name.endswith(".csv")
    )
    async def get_csv_file(message: types.Message, state: FSMContext):
        if await BotUI.teacher_domain.form_groups(message):
            await message.answer(text="Группы успешно загружены!",
                                 reply_markup=ReplyKeyboardRemove())
            await message.answer(text="Теперь нужно установить дедлайн для первой домашки:")
            await message.answer(text="Пришлите дату и время дедлайна в формате:\ndd.mm hh:mm")
            await state.set_state(TeacherBotStates.choosing_deadline)
        else:
            await message.answer(text="Что-то пошло не так, отправьте файл еще раз")

    @staticmethod
    @dp.message(TeacherBotStates.forming_group)
    async def get_csv_file_incorrectly(message: types.Message):
        await message.answer(text="Вы должны отправить файл с расширением .csv")

    # --------------------------Установка дедлайна------------------------------------
    @staticmethod
    @dp.message(TeacherBotStates.choosing_deadline)
    async def choosing_deadline(message: types.message, state: FSMContext):
        if BotUI.teacher_domain.is_deadline_correct(message.text):
            await BotUI.on_first_deadline(message.text)
            weekday = BotUI.teacher_domain.get_weekday_from_deadline(message.text)
            await message.answer(text=f"Вы успешно установили дедлайн на первую домашку на {message.text}, ({weekday})",
                                 reply_markup=TeacherDefaultKeyboard.get_keyboard())
            await state.set_state(TeacherBotStates.default_state)

        else:
            await message.answer(text="Кажется, введенный вами дедлайн некорректен")
            await message.answer(text="Введите время дедлайна в формате:\ndd.mm hh:mm")

    # -------------------------Дефолтное состояние------------------------------------
    @staticmethod
    @dp.message(
        TeacherBotStates.default_state,
        F.text == "Проверить домашку"
    )
    async def check_homework(message: types.Message, state: FSMContext):
        await message.answer("Проверка домашки", reply_markup=ReplyKeyboardRemove())
        last_practice_numbers = BotUI.teacher_domain.get_last_practice_numbers()
        homework_type = HomeworkTypes.HOMEWORK
        await state.update_data(homework_type=homework_type.value)
        await message.answer(
            "Выберите номер практики",
            reply_markup=TeacherPracticeNumbersKeyboard.get_keyboard(last_practice_numbers),
        )
        await state.set_state(TeacherBotStates.picking_practice)

    @staticmethod
    @dp.message(
        TeacherBotStates.default_state,
        F.text == "Дорешка домашки"
    )
    async def check_secondary_homework(message: types.Message, state: FSMContext):
        await message.answer("Проверка дорешки", reply_markup=ReplyKeyboardRemove())
        last_practice_numbers = BotUI.teacher_domain.get_last_practice_numbers()
        last_practice_numbers = [number - 1 for number in last_practice_numbers if number - 1 > 0]
        if len(last_practice_numbers) == 0:
            await message.answer("Дорешек еще не было, поэтому пока что проверить их нельзя :)",
                                 reply_markup=TeacherDefaultKeyboard.get_keyboard())
            return
        homework_type = HomeworkTypes.SECONDARY_HOMEWORK
        await state.update_data(homework_type=homework_type.value)
        await message.answer(
            "Выберите номер практики",
            reply_markup=TeacherPracticeNumbersKeyboard.get_keyboard(last_practice_numbers)
        )
        await state.set_state(TeacherBotStates.picking_practice)

    @staticmethod
    @dp.message(
        TeacherBotStates.default_state,
        F.text == "Проверить гробы"
    )
    async def check_coffin_homework(message: types.Message, state: FSMContext):
        await message.answer("Проверка гробов", reply_markup=ReplyKeyboardRemove())
        last_practice_numbers = BotUI.teacher_domain.get_last_practice_numbers()
        homework_type = HomeworkTypes.COFFIN_HOMEWORK
        await state.update_data(homework_type=homework_type.value)
        await message.answer(
            "Выберите номер практики",
            reply_markup=TeacherPracticeNumbersKeyboard.get_keyboard(last_practice_numbers)
        )
        await state.set_state(TeacherBotStates.picking_practice)

    @staticmethod
    @dp.message(
        TeacherBotStates.default_state,
        F.text == "Дорешка гробов"
    )
    async def check_secondary_coffin_homework(message: types.Message, state: FSMContext):
        await message.answer("Проверка дорешки гробов", reply_markup=ReplyKeyboardRemove())
        last_practice_numbers = BotUI.teacher_domain.get_last_practice_numbers()
        last_practice_numbers = [number - 1 for number in last_practice_numbers if number - 1 > 0]
        if len(last_practice_numbers) == 0:
            await message.answer("Дорешек еще не было, поэтому пока что проверить их нельзя :)",
                                 reply_markup=TeacherDefaultKeyboard.get_keyboard())
            return
        homework_type = HomeworkTypes.COFFIN_HOMEWORK
        await state.update_data(homework_type=homework_type.value)
        await message.answer(
            "Выберите номер практики",
            reply_markup=TeacherPracticeNumbersKeyboard.get_keyboard(last_practice_numbers)
        )
        await state.set_state(TeacherBotStates.picking_practice)

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_practice,
        F.data != "cancel"
    )
    async def picking_practice(callback: types.CallbackQuery, state: FSMContext):
        practice_number = int(callback.data)
        groups_keyboard = TeacherGroupKeyboard.get_keyboard()
        await state.update_data(practice_number=practice_number)
        await callback.message.edit_text(text='Выберите группу', reply_markup=groups_keyboard)
        await state.set_state(TeacherBotStates.picking_group)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_practice,
        F.data == "cancel"
    )
    async def cancel_picking_practice(callback: types.CallbackQuery, state: FSMContext):
        await state.set_data(dict())
        await callback.message.edit_reply_markup()
        await callback.message.answer("Вы вернулись к начальному состоянию", reply_markup=
                                      TeacherDefaultKeyboard.get_keyboard())
        await callback.message.delete()
        await state.set_state(TeacherBotStates.default_state)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_group,
        F.data == "cancel"
    )
    async def cancel_picking_group(callback: types.CallbackQuery, state: FSMContext):
        last_practice_numbers = BotUI.teacher_domain.get_last_practice_numbers()
        data = await state.get_data()
        if data["homework_type"] in ["Дорешка", "Гробы_со_штрафом"]:
            last_practice_numbers = [number - 1 for number in last_practice_numbers if number - 1 > 0]
        await callback.message.edit_text("Выберите номер практики",
                                         reply_markup=TeacherPracticeNumbersKeyboard.get_keyboard(last_practice_numbers))
        await state.set_state(TeacherBotStates.picking_practice)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_group,
        F.data == EvaluationMode.ALL.value
    )
    async def evaluate_all(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(evaluation_mode=EvaluationMode.ALL.value)
        data = await state.get_data()
        first_file_link, second_file_link, student_tg_id = BotUI.teacher_domain.get_first_homework(int(data["practice_number"]),
                                                                                    HomeworkTypes(data["homework_type"]))
        if first_file_link is None:
            await callback.message.answer(text="Эту домашку еще никто не сделал или все сделанные домашки проверены",
                                          reply_markup=TeacherDefaultKeyboard.get_keyboard())
            await state.set_data(dict())
            await state.set_state(TeacherBotStates.default_state)
        else:
            for file_path in [first_file_link, second_file_link]:
                if file_path:
                    homework_file = FSInputFile(file_path)
                    await callback.message.answer_document(homework_file)
            for file_path in [first_file_link, second_file_link]:
                if file_path:
                    os.remove(file_path)
            await state.update_data(student_tg_id=student_tg_id)
            await callback.message.answer("В следующем сообщении пришлите оценку этой работы")
            await state.set_state(TeacherBotStates.evaluating)
        await callback.message.edit_reply_markup()
        await callback.message.delete()
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_group,
        F.data.isdigit()
    )
    async def picking_group(callback: types.CallbackQuery, state: FSMContext):
        group = callback.data
        await state.update_data(group=group)
        await state.update_data(evaluation_mode=EvaluationMode.DEFAULT.value)
        data = await state.get_data()
        students_list_tuple = BotUI.teacher_domain.get_students_by_practice_hw_type_and_group(
            int(data["practice_number"]),
            HomeworkTypes(data["homework_type"]),
            group)
        students_list = students_list_tuple.students_list
        if len(students_list) == 0:
            await callback.message.edit_reply_markup()
            await callback.message.delete()
            await callback.message.answer(
                text="Эту домашку из выбранной группы еще никто не сделал или все домашки этого типа в этой группе проверены",
                reply_markup=TeacherDefaultKeyboard.get_keyboard())
            await state.set_data(dict())
            await state.set_state(TeacherBotStates.default_state)
        else:
            student_keyboard = TeachersStudentInlineKeyboard.get_keyboard(students_list_tuple)
            await state.update_data(student_index="0")
            await callback.message.edit_text(text='Выберите студента', reply_markup=student_keyboard)
            await state.set_state(TeacherBotStates.picking_student)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_student,
        F.data == "next"
    )
    async def picking_student_next(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        student_index = int(data["student_index"])
        students_list_tuple = BotUI.teacher_domain.get_next_students(student_index)
        await state.update_data(student_index=str(student_index + 5))
        students_keyboard = TeachersStudentInlineKeyboard.get_keyboard(students_list_tuple)
        await callback.edit_text(text='Выберите студента', reply_markup=students_keyboard)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_student,
        F.data == "back"
    )
    async def picking_student_back(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        student_index = int(data["student_index"])
        students_list_tuple = BotUI.teacher_domain.get_previous_students(student_index)
        await state.update_data(student_index=str(student_index - 5))
        students_keyboard = TeachersStudentInlineKeyboard.get_keyboard(students_list_tuple)
        await callback.edit_text(text='Выберите студента', reply_markup=students_keyboard)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_student,
        F.data == "cancel"
    )
    async def cancel_picking_student(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("Выберите группу", reply_markup=TeacherGroupKeyboard.get_keyboard())
        await state.set_state(TeacherBotStates.picking_group)
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.picking_student,
        F.data != "back" and F.data != "next" and F.data != "cancel"
    )
    async def picking_student(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        callback_data = callback.data.split(' ')
        student_tg_id = callback_data[3]
        await state.update_data(student_tg_id=student_tg_id)
        first_file_path, second_file_path = BotUI.teacher_domain.get_homework(practice_number=data["practice_number"],
                                                      student_tg_id=student_tg_id,
                                                      homework_type=HomeworkTypes(data["homework_type"]))
        for file_path in [first_file_path, second_file_path]:
            if file_path:
                homework_file = FSInputFile(file_path)
                await callback.message.answer_document(homework_file)
        for file_path in [first_file_path, second_file_path]:
            if file_path:
                os.remove(file_path)
        await callback.message.answer("В следующем сообщении пришлите оценку этой работы")
        await callback.message.edit_reply_markup()
        await callback.message.delete()
        await state.set_state(TeacherBotStates.evaluating)
        await callback.answer()

    @staticmethod
    @dp.message(
        TeacherBotStates.evaluating,
        lambda F: re.match(r'^\d+(\.\d+)?$', F.text)
    )
    async def evaluate_homework(message: types.Message, state: FSMContext):
        if float(message.text) < 0:
            await message.answer("Оценка должна быть положительным числом")
            return
        data = await state.get_data()
        BotUI.teacher_domain.evaluate_homework(data["student_tg_id"],
                                               HomeworkTypes(data["homework_type"]),
                                               data["practice_number"])
        await state.update_data(evaluation=message.text)
        await message.answer("Теперь напишите комментарий к работе")
        await state.set_state(TeacherBotStates.commenting)

    @staticmethod
    @dp.message(
        TeacherBotStates.evaluating
    )
    async def evaluate_homework_incorrectly(message: types.Message):
        await message.answer("Оценка должна быть положительным числом")

    @staticmethod
    @dp.message(
        TeacherBotStates.commenting,
        F.text
    )
    async def comment_homework(message: types.Message, state: FSMContext):
        await message.answer("Оценка и комментарий отправлены студенту",
                             reply_markup=TeacherDefaultKeyboard.get_keyboard())
        data = await state.get_data()
        await message.bot.send_message(data["student_tg_id"],
                                       f"Оценка за {data['homework_type']} {data['practice_number']}:\n{data['evaluation']}\n\nКомментарий:\n{message.text}")
        if data["evaluation_mode"] == EvaluationMode.DEFAULT.value:
            await message.answer("Выберите группу для проверки следующей работы", reply_markup=TeacherGroupKeyboard.get_keyboard())
            await state.set_state(TeacherBotStates.picking_group)
        else:
            await message.answer("Что вы хотите сделать дальше?",
                                    reply_markup=TeacherContinueEvaluationKeyboard.get_keyboard())
            await state.set_state(TeacherBotStates.evaluation_question)

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.evaluation_question,
        F.data == "continue"
    )
    async def continue_evaluation(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        first_file_link, second_file_link, student_tg_id = BotUI.teacher_domain.get_first_homework(
            int(data["practice_number"]),
            HomeworkTypes(data["homework_type"]))
        if first_file_link is None:
            await callback.message.answer(text=f"Вы проверили все сданные домашки типа {data['homework_type']} за {data['practice_number']} практику",
                                          reply_markup=TeacherDefaultKeyboard.get_keyboard())
            await state.set_data(dict())
            await state.set_state(TeacherBotStates.default_state)
        else:
            for file_path in [first_file_link, second_file_link]:
                if file_path:
                    homework_file = FSInputFile(file_path)
                    await callback.message.answer_document(homework_file)
            for file_path in [first_file_link, second_file_link]:
                if file_path:
                    os.remove(file_path)
            await state.update_data(student_tg_id=student_tg_id)
            await callback.message.answer("В следующем сообщении пришлите оценку этой работы")
            await state.set_state(TeacherBotStates.evaluating)
        await callback.message.edit_reply_markup()
        await callback.message.delete()
        await callback.answer()

    @staticmethod
    @dp.callback_query(
        TeacherBotStates.evaluation_question,
        F.data == "break"
    )
    async def break_evaluation(callback: types.CallbackQuery, state: FSMContext):
        await state.set_data(dict())
        await callback.message.edit_reply_markup()
        await callback.message.delete()
        await callback.message.answer("Проверка прекращена", reply_markup=TeacherDefaultKeyboard.get_keyboard())
        await state.set_state(TeacherBotStates.default_state)
        await callback.answer()

    @staticmethod
    @dp.message(
        TeacherBotStates.commenting
    )
    async def comment_homework_incorrectly(message: types.Message):
        await message.answer("Оставьте, пожалуйста, текстовый комментарий к работе")

    #--------------------------------------------------------------
    #----------------------Студент---------------------------------
    @staticmethod
    @dp.message(
        AuthorizationBotStates.choose_role,
        F.text == "Я студент"
    )
    async def start_handler_student(message: types.Message, state: FSMContext):
        if BotUI.student_domain.try_find_student_by_tg_id(str(message.from_user.id)):
            await message.answer(text="Отлично! Теперь выберите, что вы хотите сделать",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        elif not BotUI.teacher_domain.is_students_database_filled():
            await message.answer("Преподаватель еще не сформировал списки групп. Попробуйте авторизоваться позже",
                                 reply_markup=AuthorizationDefaultKeyboard.get_keyboard())
        else:
            await message.answer("Вас нет в списке студентов. Обратитесь к вашему преподавателю практики, после чего снова пройдите авторизацию",
                                 reply_markup=AuthorizationDefaultKeyboard.get_keyboard())

    @staticmethod
    @dp.message(
        StudentBotStates.default_state,
        F.text == "Сдать домашку")
    async def default_handler_student(message: types.Message, state: FSMContext):
        practice_number = BotUI.teacher_domain.get_current_practice_number()
        if BotUI.student_domain.try_find_homework(str(message.from_user.id), HomeworkTypes.HOMEWORK, practice_number):
            await message.answer("Вы уже сдали эту домашку, второй раз сдать не получится :)",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        else:
            await state.update_data(practice_number=practice_number)
            await state.update_data(homework_type=HomeworkTypes.HOMEWORK.value)
            await message.answer(text="Пришлите .pdf файл с вашей домашкой",
                                 reply_markup=StudentCancelKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.upload_state_homework)

    @staticmethod
    @dp.message(
        StudentBotStates.default_state,
        F.text == "Дорешка домашки")
    async def default_handler_student(message: types.Message, state: FSMContext):
        practice_number = BotUI.teacher_domain.get_current_practice_number() - 1
        if practice_number < 1:
            await message.answer("Дорешек еще нет, сейчас можно сдать только домашку",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        elif BotUI.student_domain.try_find_homework(str(message.from_user.id), HomeworkTypes.SECONDARY_HOMEWORK, practice_number):
            await message.answer("Вы уже сдали эту дорешку, второй раз сдать не получится :)",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        else:
            await state.update_data(practice_number=practice_number)
            await state.update_data(homework_type=HomeworkTypes.SECONDARY_HOMEWORK.value)
            await message.answer(text="Пришлите .pdf файл с вашей домашкой",
                             reply_markup=StudentCancelKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.upload_state_homework)

    @staticmethod
    @dp.message(
        StudentBotStates.default_state,
        F.text == "Сдать гробы")
    async def default_handler_student(message: types.Message, state: FSMContext):
        practice_number = BotUI.teacher_domain.get_current_practice_number()
        if BotUI.student_domain.try_find_homework(str(message.from_user.id), HomeworkTypes.COFFIN_HOMEWORK, practice_number):
            await message.answer("Вы уже сдали эти гробы, второй раз сдать не получится :)",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        else:
            await state.update_data(practice_number=practice_number)
            await state.update_data(homework_type=HomeworkTypes.COFFIN_HOMEWORK.value)
            await message.answer(text="Пришлите .pdf файл с вашей домашкой",
                             reply_markup=StudentCancelKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.upload_state_homework)

    @staticmethod
    @dp.message(
        StudentBotStates.default_state,
        F.text == "Дорешка гробов")
    async def default_handler_student(message: types.Message, state: FSMContext):
        practice_number = BotUI.teacher_domain.get_current_practice_number() - 1
        if practice_number < 1:
            await message.answer("Дорешек еще нет, сейчас можно сдать только домашку",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        elif BotUI.student_domain.try_find_homework(str(message.from_user.id), HomeworkTypes.SECONDARY_COFFIN_HOMEWORK,
                                                    practice_number):
            await message.answer("Вы уже сдали эту дорешку, второй раз сдать не получится :)",
                                 reply_markup=StudentDefaultKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.default_state)
        else:
            await state.update_data(homework_type=HomeworkTypes.SECONDARY_COFFIN_HOMEWORK.value)
            await state.update_data(practice_number=practice_number)
            await message.answer(text="Пришлите .pdf файл с вашей домашкой",
                             reply_markup=StudentCancelKeyboard.get_keyboard())
            await state.set_state(StudentBotStates.upload_state_homework)

    @staticmethod
    @dp.message(
        StudentBotStates.upload_state_homework,
        F.text == "Отмена"
    )
    async def cancel_upload_homework(message: types.Message, state: FSMContext):
        await message.answer("Вы вернулись в предыдущее состояние",
                             reply_markup=StudentDefaultKeyboard.get_keyboard())
        await state.set_state(StudentBotStates.default_state)

    @staticmethod
    @dp.message(
        StudentBotStates.upload_state_homework,
        F.document.file_name.endswith(".pdf")
    )
    async def upload_homework_handler_student(message: types.Message, state: FSMContext):
        data = await state.get_data()
        homework_type = HomeworkTypes(data["homework_type"])
        practice_number = int(data["practice_number"])
        await BotUI.student_domain.upload_homework_file(message, homework_type, practice_number)
        await message.answer(text='Теперь загрузите .py файл или нажмите кнопку "Отправить без .py файла"',
                             reply_markup=StudentPythonFileKeyboard.get_keyboard())
        await state.set_state(StudentBotStates.upload_python_file)

    @staticmethod
    @dp.message(
        StudentBotStates.upload_python_file,
        F.text == "Отправить без .py файла"
    )
    async def continue_without_py_file(message: types.Message, state: FSMContext):
        await message.answer("Работа была успешно загружена!",
                             reply_markup=StudentDefaultKeyboard.get_keyboard())
        await state.set_data(dict())
        await state.set_state(StudentBotStates.default_state)

    @staticmethod
    @dp.message(
        StudentBotStates.upload_python_file,
        F.document.file_name.endswith(".py")
    )
    async def upload_py_file(message: types.Message, state: FSMContext):
        data = await state.get_data()
        await BotUI.student_domain.add_py_file_to_homework(message, int(data["practice_number"]),
                                                     HomeworkTypes(data["homework_type"]))
        await state.set_data(dict())
        await message.answer("Работа была успешно загружена!",
                             reply_markup=StudentDefaultKeyboard.get_keyboard())
        await state.set_state(StudentBotStates.default_state)

    @staticmethod
    @dp.message(
        StudentBotStates.upload_python_file
    )
    async def upload_py_file(message: types.Message):
        await message.answer('Пришлите файл с расширением .py или нажмите на кнопку "Отправить без .py файла"')

    @staticmethod
    @dp.message(
        StudentBotStates.default_state
    )
    async def get_incorrect_text(message: types.Message):
        await message.answer(text="Пожалуйста, выберите команду из предложенных ниже")

    @staticmethod
    @dp.message(
        StudentBotStates.upload_state_homework
    )
    async def ask_file_incorrectly(message: types.Message):
        await message.answer(text="Нужен .pdf файл")

    # --------------- Дедлайны -----------------------------------------
    @staticmethod
    async def on_first_deadline(message_text: str):
        BotUI.teacher_domain.set_first_deadline(message_text)
        deadline_datetime = BotUI.teacher_domain.get_deadline_datetime(message_text)
        BotUI.scheduler.add_job(BotUI.on_deadline_change, "date", run_date=deadline_datetime)

    @staticmethod
    async def on_deadline_change():
        next_deadline_datetime = BotUI.teacher_domain.get_next_deadline()
        BotUI.teacher_domain.update_homework_info()
        await BotUI.send_notification_of_changed_deadline()
        BotUI.scheduler.add_job(BotUI.on_deadline_change, "date", run_date=next_deadline_datetime)

    @staticmethod
    async def send_notification_of_changed_deadline():
        all_students_ids = BotUI.teacher_domain.get_all_students_ids()
        current_practice_number = BotUI.teacher_domain.get_current_practice_number()
        current_deadline = BotUI.teacher_domain.get_current_deadline().strftime("%d.%m %H:%M")
        for student_id in all_students_ids:
            await BotUI.bot.send_message(student_id, f"Дедлайн для сдачи практики {current_practice_number - 1} прошел,\nДедлайн для сдачи практики {current_practice_number}: {current_deadline}")

    @staticmethod
    async def update_scheduler_on_last_deadline():
        deadline_datetime = BotUI.teacher_domain.get_current_deadline()
        BotUI.scheduler.add_job(BotUI.on_deadline_change, "date", run_date=deadline_datetime)
