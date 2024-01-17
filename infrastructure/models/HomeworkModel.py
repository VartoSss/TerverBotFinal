from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.DBConfig import AbstractModel


class HomeworkModel(AbstractModel):
    __tablename__ = 'homeworks'
    student_tg_id: Mapped[str] = mapped_column(VARCHAR(30), ForeignKey('students.telegram_id'),
                                               nullable=False)
    file_link: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    second_file_link: Mapped[str] = mapped_column(VARCHAR, nullable=True)
    file_name: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    homework_type: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    practice_number: Mapped[int] = mapped_column(nullable=False)
    evaluated: Mapped[bool] = mapped_column(nullable=False)
