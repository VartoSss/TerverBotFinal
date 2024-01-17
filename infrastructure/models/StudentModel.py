from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.DBConfig import AbstractModel


class StudentModel(AbstractModel):
    __tablename__ = 'students'
    telegram_id: Mapped[str] = mapped_column(VARCHAR(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    surname: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    student_group: Mapped[int] = mapped_column(nullable=False)
