from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.DBConfig import AbstractModel


class HomeworkInfoModel(AbstractModel):
    __tablename__ = 'homework_info'
    current_practice: Mapped[int] = mapped_column(nullable=False)
    homework_deadline = mapped_column(DateTime())
    secondary_homework_deadline = mapped_column(DateTime())
