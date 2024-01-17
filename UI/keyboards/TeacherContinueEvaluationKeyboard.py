from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram import types
from Enums.HomeworkTypes import HomeworkTypes


class TeacherContinueEvaluationKeyboard:
    @staticmethod
    def get_keyboard() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="Продолжить проверку", callback_data="continue"))
        builder.row(types.InlineKeyboardButton(text="Прекратить проверку", callback_data="break"))
        return builder.as_markup()
