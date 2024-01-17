from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


class TeacherChoosingDeadlineDayKeyboard:
    _weekdays = ["Понедельник", "Вторник", "Среда", "Четверг",
                 "Пятница", "Суббота", "Воскресенье"]

    @staticmethod
    def get_keyboard():
        builder = InlineKeyboardBuilder()
        for weekday in TeacherChoosingDeadlineDayKeyboard._weekdays:
            builder.row(types.InlineKeyboardButton(
                text=weekday,
                callback_data=weekday
            ))
        return builder.as_markup()
