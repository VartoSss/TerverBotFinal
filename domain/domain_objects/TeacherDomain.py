import os
from aiogram.types import Message
from domain.domain_objects.CSVParser import CSVParser
from infrastructure.repositories.HomeworkRepository import *
from infrastructure.repositories.StudentRepository import *
from infrastructure.repositories.HomeworkInfoRepository import *
from domain.GoogleDriveVars import GoogleDriveVars
from domain.StudentsListTuple import StudentsListTuple
from datetime import datetime, timedelta


class TeacherDomain:
    def __init__(self):
        self._students = []
        self._timezone = "Asia/Yekaterinburg"
        self._homework_repository = HomeworkRepository()
        self._student_repository = StudentRepository()
        self._homework_info_repository = HomeworkInfoRepository()
        #For testing
        self.delta = timedelta(minutes=2)

    def get_students_by_practice_hw_type_and_group(self, practice_number: int, homework_type: HomeworkTypes, group: str) -> StudentsListTuple:
        self._students = self._student_repository.get_students_by_practice_hw_type_and_group(practice_number, homework_type, group)
        can_look_next = len(self._students) > 5
        return StudentsListTuple(self._students[0 : 5], False, can_look_next)

    def get_first_homework(self, practice_number: int, homework_type: HomeworkTypes) -> (str, str, str):
        homework = self._homework_repository.get_first_homework(practice_number, homework_type)
        if homework is None:
            return None, None, None
        first_file_link, second_file_link, file_name, student_tg_id = homework
        first_local_file_link = self.__get_file_from_drive(first_file_link, file_name, practice_number, ".pdf")
        second_local_file_link = self.__get_file_from_drive(second_file_link, file_name, practice_number, ".py")
        return first_local_file_link, second_local_file_link, student_tg_id

    def get_next_students(self, student_index: int) -> StudentsListTuple:
        can_look_next = len(self._students) - student_index > 0
        return StudentsListTuple(self._students[student_index : student_index + 5], True, can_look_next)

    def get_previous_students(self, student_index: int) -> StudentsListTuple:
        can_look_back = student_index >= 5
        return StudentsListTuple(self._students[student_index : student_index + 5], can_look_back, True)

    def get_homework(self, practice_number: int, student_tg_id: str, homework_type: HomeworkTypes) -> (str, str):
        first_file_link, second_file_link, file_name = self._homework_repository.get_homework_links_and_name(student_tg_id, practice_number, homework_type)
        first_local_file_link = self.__get_file_from_drive(first_file_link, file_name, practice_number, ".pdf")
        second_local_file_link = self.__get_file_from_drive(second_file_link, file_name, practice_number, ".py")
        return first_local_file_link, second_local_file_link

    def update_homework_info(self):
        current_practice_number = self._homework_repository.get_current_practice_number()
        next_practice_number = current_practice_number + 1
        current_deadline = self._homework_info_repository.get_current_deadline()
        next_deadline = current_deadline + self.delta
        next_secondary_deadline = next_deadline + self.delta
        self._homework_info_repository.update_homework_info(current_practice_number, next_practice_number, next_deadline, next_secondary_deadline)

    def get_all_students_ids(self):
        return self._student_repository.get_all_students_ids()

    async def form_groups(self, message: Message) -> bool:
        file = await message.bot.get_file(message.document.file_id)
        local_file_path = f"{os.getcwd()}\\hw_{message.from_user.id}.csv"
        await message.bot.download_file(file.file_path, local_file_path)
        try:
            student_list = CSVParser.parse(local_file_path)
            self._student_repository.form_student_table(student_list)
            os.remove(local_file_path)
            return True
        except Exception as _ex:
            return False

    def create_database(self):
        self._student_repository.create_database()
        self._homework_info_repository.add_homework_info()

    def is_students_database_filled(self) -> bool:
        return len(self._student_repository.try_find_student()) > 0
    
    def is_homework_info_database_filled(self) -> bool:
        return self._homework_info_repository.get_current_deadline() is not None

    def add_student(self, name: str, surname: str, group: str, tg_id: str) -> None:
        return self._student_repository.add_student(name, surname, group, tg_id)

    def get_last_practice_numbers(self) -> list[int]:
        current_practice_number = self._homework_repository.get_current_practice_number()
        result_list = [current_practice_number - 3, current_practice_number -
                       2, current_practice_number - 1, current_practice_number]
        return [number for number in result_list if number > 0]
    
    def is_deadline_correct(self, deadline: str) -> bool:
        try:
            datetime.strptime(deadline, "%d.%m %H:%M")
            return True
        except ValueError:
            return False
        
    def get_weekday_from_deadline(self, deadline: str) -> str:
        deadline_datetime = self.get_deadline_datetime(deadline)
        day_of_week = deadline_datetime.weekday()
        weekdays = [
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье"
        ]
        return weekdays[day_of_week]
    
    def get_deadline_datetime(self, deadline: str):
        current_year = datetime.now().year
        return datetime.strptime(f"{current_year} {deadline}", "%Y %d.%m %H:%M")

    def get_current_deadline(self) -> datetime:
        return self._homework_info_repository.get_current_deadline()

    def get_next_deadline(self) -> datetime:
        return self._homework_info_repository.get_next_deadline()

    def set_first_deadline(self, deadline: str) -> None:
        deadline_datetime = self.get_deadline_datetime(deadline)
        secondary_deadline_datetime = deadline_datetime + self.delta
        self._homework_info_repository.change_homework_info_deadline(1, deadline_datetime, secondary_deadline_datetime)

    def change_deadline(self) -> None:
        pass

    def __update_deadlines(self) -> None:
        pass

    def get_current_practice_number(self) -> int:
        return self._homework_repository.get_current_practice_number()

    def __get_student_tg_id_by_full_name_and_group(self, name: str, surname: str, group: str) -> str:
        return self._student_repository.get_student_tg_id_by_full_name_and_group(name, surname, group)

    def get_all_students_ids(self):
        return self._student_repository.get_all_students_ids()

    def __get_file_from_drive(self, file_link: str, file_name: str, practice_number: int, extension: str) -> str:
        folder_name = f"HW{practice_number}"
        folder_id = GoogleDriveVars.FOLDERS_NAME_TO_ID[folder_name]
        try:
            file_list = GoogleDriveVars.DRIVE.ListFile(
                {'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
            for file in file_list:
                if file['alternateLink'] == file_link:
                    local_file_path = f"{os.getcwd()}\\{file_name}{extension}"
                    with open(local_file_path, "wb"):
                        file.GetContentFile(local_file_path)
                    return local_file_path
        except Exception as _ex:
            print(f"There was an exception due to Google Drive connection: {_ex}")

    def evaluate_homework(self, student_tg_id: str, homework_type: HomeworkTypes, practice_number: str):
        self._homework_repository.evaluate_homework(student_tg_id, homework_type, practice_number)
