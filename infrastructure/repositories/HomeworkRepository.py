from sqlalchemy import *
from Enums.HomeworkTypes import HomeworkTypes
from sqlalchemy.orm import Session
from infrastructure.models.StudentModel import StudentModel
from infrastructure.models.HomeworkModel import HomeworkModel
from infrastructure.models.HomeworkInfoModel import HomeworkInfoModel
from infrastructure.DBConfig import DBConfig


class HomeworkRepository:
    def get_current_practice_number(self) -> int:
        with Session(DBConfig.engine) as session:
            with session.begin():
                current_practice = session.scalar(select(HomeworkInfoModel)).current_practice
                return current_practice

    def get_first_homework(self, practice_number: int, homework_type: HomeworkTypes) -> (str, str, str):
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = session.query(HomeworkModel.file_link, HomeworkModel.second_file_link,
                                         HomeworkModel.file_name, HomeworkModel.student_tg_id) \
                    .filter(
                        and_(HomeworkModel.practice_number == practice_number,
                        HomeworkModel.homework_type == homework_type.value,
                        HomeworkModel.evaluated == False
                    )).first()
                return homework

    def get_homework_links_and_name(self, student_tg_id: str, practice_number: int, homework_type: HomeworkTypes) -> (str, str):
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = session.query(HomeworkModel.file_link, HomeworkModel.second_file_link, HomeworkModel.file_name) \
                    .join(StudentModel, HomeworkModel.student_tg_id == StudentModel.telegram_id) \
                    .filter(
                        and_(StudentModel.telegram_id == student_tg_id,
                        HomeworkModel.practice_number == practice_number,
                        HomeworkModel.homework_type == homework_type.value,
                        HomeworkModel.evaluated == False
                    )).one()
                return homework

    def add_homework(self, student_tg_id: str, file_link: str, file_name: str, practice_number: int, homework_type: HomeworkTypes) -> None:
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = HomeworkModel(student_tg_id=student_tg_id, file_link=file_link, file_name=file_name,
                                         homework_type=homework_type.value, practice_number=practice_number,
                                         evaluated=False)
                session.add(homework)

    def add_py_file_to_homework(self, student_tg_id: str, practice_number: int, homework_type: HomeworkTypes, file_link: str):
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = session.query(HomeworkModel).filter(
                    and_(HomeworkModel.homework_type == homework_type.value,
                    HomeworkModel.student_tg_id == student_tg_id,
                    HomeworkModel.practice_number == practice_number
                )).one()
                homework.second_file_link = file_link

    def find_homework(self, student_tg_id: str, homework_type: HomeworkTypes, practice_number: int) -> HomeworkModel | None:
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = session.query(HomeworkModel).filter(
                    and_(HomeworkModel.homework_type == homework_type.value,
                    HomeworkModel.practice_number == practice_number,
                    HomeworkModel.student_tg_id == student_tg_id,
                )).one_or_none()
                return homework

    def evaluate_homework(self, student_tg_id: str, homework_type: HomeworkTypes, practice_number: str) -> None:
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework = session.query(HomeworkModel).filter(
                    and_(HomeworkModel.homework_type == homework_type.value,
                    HomeworkModel.practice_number == practice_number,
                    HomeworkModel.student_tg_id == student_tg_id,
                    HomeworkModel.evaluated == False
                )).one()
                homework.evaluated = True
