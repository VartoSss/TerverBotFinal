from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from aiogram import types
from Enums.HomeworkTypes import HomeworkTypes


class StudentPythonFileKeyboard:
    @staticmethod
    def get_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text="Отправить без .py файла")
        )
        return builder.as_markup(resize_keyboard=True)
