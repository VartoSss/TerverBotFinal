from sqlalchemy import *
from Enums.HomeworkTypes import HomeworkTypes
from sqlalchemy.orm import Session
from infrastructure.models.StudentModel import StudentModel
from infrastructure.models.HomeworkModel import HomeworkModel
from infrastructure.models.HomeworkInfoModel import HomeworkInfoModel
from infrastructure.DBConfig import DBConfig


class StudentRepository:
    def add_student(self, name: str, surname: str, group: str, student_tg_id: str) -> None:
        pass

    def get_student_full_name_and_group_by_tg_id(self, student_tg_id: str) -> (str, str, str):
        with Session(DBConfig.engine) as session:
            with session.begin():
                student = session.scalar(select(StudentModel).where(StudentModel.telegram_id == student_tg_id))
                return student.name, student.surname, str(student.student_group)

    def get_student_tg_id_by_full_name_and_group(self, name: str, surname: str, group: str) -> str:
        with Session(DBConfig.engine) as session:
            with session.begin():
                student = session.scalar(select(StudentModel).where(and_(StudentModel.name == name,
                                                                         StudentModel.surname == surname,
                                                                         StudentModel.student_group == int(group))))
                return student.telegram_id

    def get_students_by_practice_hw_type_and_group(self, practice_number: int, homework_type: HomeworkTypes, group: str) -> list[str]:
        result = []
        with Session(DBConfig.engine) as session:
            with session.begin():
                if group == "300":
                    students = session.query(StudentModel) \
                        .join(HomeworkModel, StudentModel.telegram_id == HomeworkModel.student_tg_id) \
                        .filter(and_(HomeworkModel.homework_type == homework_type.value,
                                     HomeworkModel.practice_number == practice_number,
                                     StudentModel.student_group > int(group),
                                     HomeworkModel.evaluated == False)).all()
                else:
                    students = session.query(StudentModel) \
                        .join(HomeworkModel, StudentModel.telegram_id == HomeworkModel.student_tg_id) \
                        .filter(and_(HomeworkModel.homework_type == homework_type.value,
                                     HomeworkModel.practice_number == practice_number,
                                     StudentModel.student_group == int(group),
                                     HomeworkModel.evaluated == False)).all()
                for student in students:
                    result.append(f"{student.surname} {student.name} {student.student_group} {student.telegram_id}")
        return result

    def create_database(self) -> None:
        DBConfig.create_all()

    def get_student_by_tg_id(self, student_tg_id: str) -> StudentModel | None:
        with Session(DBConfig.engine) as session:
            with session.begin():
                student = session.query(StudentModel)\
                    .filter(StudentModel.telegram_id == student_tg_id)\
                    .one_or_none()
                return student

    def try_find_student(self) -> list[StudentModel]:
        with Session(DBConfig.engine) as session:
            with session.begin():
                student = session.query(StudentModel).all()
                return student
            
    def get_all_students_ids(self) -> list[int]:
        with Session(DBConfig.engine) as session:
            with session.begin():
                students = session.query(StudentModel).all()
                return [int(student.telegram_id) for student in students]

    def form_student_table(self, students_list: list[list[str]]) -> None:
        with Session(DBConfig.engine) as session:
            for student_info in students_list:
                tg_id, name, surname, group = student_info[0], student_info[1], student_info[2], \
                    int(student_info[3])
                with session.begin():
                    student = StudentModel(telegram_id=tg_id, name=name, surname=surname, student_group=group)
                    session.add(student)
