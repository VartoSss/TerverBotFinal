from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram import types
from Enums.HomeworkTypes import HomeworkTypes


class TeacherPracticeNumbersKeyboard:
    @staticmethod
    def get_keyboard(practices_list) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for practice in practices_list:
            builder.add(types.InlineKeyboardButton(
                text=f"{practice}",
                callback_data=f"{practice}"
            ))
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="cancel"
        ))
        builder.adjust(1)
        return builder.as_markup()
