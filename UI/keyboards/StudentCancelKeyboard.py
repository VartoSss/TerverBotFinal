from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from aiogram import types
from Enums.HomeworkTypes import HomeworkTypes


class StudentCancelKeyboard:
    @staticmethod
    def get_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text="Отмена")
        )
        return builder.as_markup(resize_keyboard=True)
