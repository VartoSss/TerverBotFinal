from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class StudentDefaultKeyboard:
    @staticmethod
    def get_keyboard():
        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text="Сдать домашку"),
            types.KeyboardButton(text="Дорешка домашки")
        )
        builder.row(
            types.KeyboardButton(text="Сдать гробы"),
            types.KeyboardButton(text="Дорешка гробов")
        )
        return builder.as_markup(resize_keyboard=True)
