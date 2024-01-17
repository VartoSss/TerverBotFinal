from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class TeacherDefaultKeyboard:
    @staticmethod
    def get_keyboard():
        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text="Проверить домашку"),
            types.KeyboardButton(text="Дорешка домашки")
        )
        builder.row(
            types.KeyboardButton(text="Проверить гробы"),
            types.KeyboardButton(text="Дорешка гробов")
        )
        return builder.as_markup(resize_keyboard=True)
