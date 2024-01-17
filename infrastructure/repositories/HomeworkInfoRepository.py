from datetime import datetime
from sqlalchemy import *
from sqlalchemy import *
from Enums.HomeworkTypes import HomeworkTypes
from sqlalchemy.orm import Session
from infrastructure.models.StudentModel import StudentModel
from infrastructure.models.HomeworkModel import HomeworkModel
from infrastructure.models.HomeworkInfoModel import HomeworkInfoModel
from infrastructure.DBConfig import DBConfig


class HomeworkInfoRepository:
    def add_homework_info(self):
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework_info = session \
                        .query(HomeworkInfoModel) \
                        .one_or_none()
                if homework_info is not None:
                    return
                homework_info = HomeworkInfoModel(current_practice=1)
                session.add(homework_info)

    def get_current_deadline(self):
        with Session(DBConfig.engine) as session:
            with session.begin():
                current_deadline = session.query(HomeworkInfoModel).first()
                if current_deadline.homework_deadline is not None:
                    return datetime.fromtimestamp(current_deadline.homework_deadline.timestamp())
                return None

    def get_next_deadline(self):
        with Session(DBConfig.engine) as session:
            with session.begin():
                next_deadline = session.query(HomeworkInfoModel).first()
                return datetime.fromtimestamp(next_deadline.secondary_homework_deadline.timestamp())

    def change_homework_info_deadline(self, practice_number: int, homework_deadline: datetime, secondary_homework_deadline: datetime):
        with Session(DBConfig.engine) as session:
            with session.begin():
                homework_info = session \
                    .query(HomeworkInfoModel) \
                    .filter(HomeworkInfoModel.current_practice == practice_number) \
                    .first()
                homework_info.homework_deadline = homework_deadline
                homework_info.secondary_homework_deadline = secondary_homework_deadline
                session.commit()

    def update_homework_info(self, current_practice_number: int, 
                             next_practice_number: int, 
                             homework_deadline: datetime, 
                             secondary_homework_deadline: datetime):

        with Session(DBConfig.engine) as session:
            with session.begin():
                homework_info = session \
                    .query(HomeworkInfoModel) \
                    .filter(HomeworkInfoModel.current_practice == current_practice_number) \
                    .first()
                homework_info.current_practice = next_practice_number
                homework_info.homework_deadline = homework_deadline
                homework_info.secondary_homework_deadline = secondary_homework_deadline
                session.commit()
