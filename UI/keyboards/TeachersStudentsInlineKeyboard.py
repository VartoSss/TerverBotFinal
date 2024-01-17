from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from domain.StudentsListTuple import StudentsListTuple
from Enums.HomeworkTypes import HomeworkTypes


class TeachersStudentInlineKeyboard:
    @staticmethod
    def get_keyboard(students_list_tuple: StudentsListTuple):
        builder = InlineKeyboardBuilder()
        students_to_display = students_list_tuple.students_list
        for student in students_to_display:
            text = " ".join(student.split(" ")[:-2])
            builder.row(types.InlineKeyboardButton(
                text=text,
                callback_data=f"{student}"
            ))
        if students_list_tuple.is_next and students_list_tuple.is_back:
            builder.row(
                types.InlineKeyboardButton(
                    text="Далее",
                    callback_data=f"next"
                ),
                types.InlineKeyboardButton(
                    text="Назад",
                    callback_data=f"back"
                ))
        elif students_list_tuple.is_next:
            builder.row(types.InlineKeyboardButton(
                text="Далее",
                callback_data=f"next"
            ))
        elif students_list_tuple.is_back:
            builder.row(types.InlineKeyboardButton(
                text="Назад",
                callback_data=f"back"
            ))
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="cancel"
        ))
        builder.adjust(1)
        return builder.as_markup()
