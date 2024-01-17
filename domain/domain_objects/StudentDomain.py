import os
from aiogram.types import Message
from infrastructure.repositories.HomeworkRepository import *
from infrastructure.repositories.StudentRepository import *
from domain.GoogleDriveVars import GoogleDriveVars


class StudentDomain:
    def __init__(self):
        self._homework_repository = HomeworkRepository()
        self._student_repository = StudentRepository()

    async def upload_homework_file(self, message: Message, homework_type: HomeworkTypes, practice_number: int) -> None:
        file = await message.bot.get_file(message.document.file_id)
        local_file_path = f"{os.getcwd()}\\{homework_type.value}_{practice_number}_{message.from_user.id}.pdf"
        await message.bot.download_file(file.file_path, local_file_path)
        student_name, student_surname, student_group = self._student_repository.get_student_full_name_and_group_by_tg_id(str(message.from_user.id))
        file_name = self.__create_homework_file_name(student_name, student_surname, student_group, homework_type, practice_number)
        drive_file_link = self.__upload_file_to_drive(local_file_path, file_name, practice_number, homework_type)
        self.__add_homework(drive_file_link, file_name, practice_number, homework_type, str(message.from_user.id))
        os.remove(local_file_path)

    def __create_homework_file_name(self, student_name: str, student_surname: str, group: str, homework_type: HomeworkTypes, practice_number: int) -> str:
        return f"{student_surname}_{student_name}_ФТ-{group}_{homework_type.value}_{practice_number}"

    def __upload_file_to_drive(self, file_link: str, file_name: str, practice_number: int, homework_type: HomeworkTypes) -> str:
        number_practice_in_file = self.__get_practice_number_by_file_name(file_name)
        if not self.__is_hw_folder_exists(folder_name=f"HW{number_practice_in_file}"):
            self.__create_hw_folder_drive(number_practice_in_file)
        folder_id = GoogleDriveVars.FOLDERS_NAME_TO_ID[f"HW{number_practice_in_file}"]
        file_metadata = {
            'title': f'{file_name}',
            'parents': [{'id': folder_id}]
        }
        try:
            file_hw = GoogleDriveVars.DRIVE.CreateFile(file_metadata)
            file_hw.SetContentFile(file_link)
            file_hw.Upload()
            file_link = file_hw['alternateLink']
            file_hw = None
            return file_link
        except Exception as _ex:
            print(f"There was an exception due to Google Drive connection: {_ex}")

    def __add_homework(self, file_link: str, file_name: str, practice_number: int, homework_type: HomeworkTypes, student_tg_id: str) -> None:
        self._homework_repository.add_homework(student_tg_id, file_link, file_name, practice_number, homework_type)

    async def add_py_file_to_homework(self, message: Message, practice_number: int, homework_type: HomeworkTypes):
        file = await message.bot.get_file(message.document.file_id)
        local_file_path = f"{os.getcwd()}\\{homework_type.value}_{practice_number}_{message.from_user.id}.py"
        await message.bot.download_file(file.file_path, local_file_path)
        student_name, student_surname, student_group = self._student_repository.get_student_full_name_and_group_by_tg_id(str(message.from_user.id))
        file_name = self.__create_homework_file_name(student_name, student_surname, student_group, homework_type,
                                                     practice_number)
        drive_file_link = self.__upload_file_to_drive(local_file_path, file_name, practice_number, homework_type)
        self._homework_repository.add_py_file_to_homework(str(message.from_user.id), practice_number, homework_type, drive_file_link)
        os.remove(local_file_path)

    def try_find_student_by_tg_id(self, student_tg_id: str) -> bool:
        return self._student_repository.get_student_by_tg_id(student_tg_id) is not None

    def try_find_homework(self, student_tg_id: str, homework_type: HomeworkTypes, practice_number: int) -> bool:
        return self._homework_repository.find_homework(student_tg_id, homework_type, practice_number) is not None

    def __get_practice_number_by_file_name(self, file_name: str) -> int:
        return int(file_name.split('_')[4])
    
    def __is_hw_folder_exists(self, folder_name: str) -> bool:
        folder_list = GoogleDriveVars.DRIVE.ListFile(
            {'q': f"'root' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
        return len(folder_list) > 0

    def __create_hw_folder_drive(self, practice_number: int) -> None:
        folder_name = f"HW{practice_number}"
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        try:
            folder = GoogleDriveVars.DRIVE.CreateFile(folder_metadata)
            folder.Upload()
            GoogleDriveVars.FOLDERS_NAME_TO_ID[folder_name] = str(folder['id'])
        except Exception as _ex:
            print(f"There was an exception due to Google Drive connection: {_ex}")
