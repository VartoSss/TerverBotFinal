from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram import types
from Enums.EvaluationMode import EvaluationMode


class TeacherGroupKeyboard:
    @staticmethod
    def get_keyboard() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="ФТ-201", callback_data="201"),
            types.InlineKeyboardButton(text="ФТ-202", callback_data="202")
        )
        builder.row(
            types.InlineKeyboardButton(text="ФТ-203", callback_data="203"),
            types.InlineKeyboardButton(text="ФТ-204", callback_data="204")
        )
        builder.row(types.InlineKeyboardButton(text="3 курс", callback_data="300"))
        builder.row(types.InlineKeyboardButton(text="Все подряд", callback_data=EvaluationMode.ALL.value))
        builder.row(types.InlineKeyboardButton(text="Отмена",callback_data="cancel"))
        return builder.as_markup()
