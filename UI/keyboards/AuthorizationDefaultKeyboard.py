from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class AuthorizationDefaultKeyboard:
    options = ["Я преподаватель", "Я студент"]

    @staticmethod
    def get_keyboard():
        kb = [
            [types.KeyboardButton(text=AuthorizationDefaultKeyboard.options[0])],
            [types.KeyboardButton(text=AuthorizationDefaultKeyboard.options[1])]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        return keyboard


        '''builder = ReplyKeyboardBuilder()
        for option in AuthorisationDefaultKeyboard.options:
            builder.add(types.KeyboardButton(text=f"{option}"))
            builder.adjust(2)
            return builder.as_markup(resize_keyboard=True)
        '''