"""Модуль команд бота."""
from telebot import types
from typing import Optional


class BotKeyboard:
    """Класс, описывающий команды бота."""

    def __init__(self, keyboard_id: str, keyboard: Optional[types.InlineKeyboardMarkup] = None):
        self.keyboard_id = keyboard_id
        self.keyboard = keyboard

    def set_keyboard(self, keyboard: types.InlineKeyboardMarkup):
        """Устанавливает клавиатуру."""
        self.keyboard = keyboard


class StartKeyboard(BotKeyboard):
    """
        Стартовая клавиатура бота.
        id: 'start',
        Кнопки: [add_expenses, add_income, reports].
    """

    def __init__(self):
        super().__init__(keyboard_id='start')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Внести расход", callback_data='add_expenses'),
            types.InlineKeyboardButton("Внести доход", callback_data='add_income'),
            types.InlineKeyboardButton("Отчеты", callback_data='reports'),
        )
        self.set_keyboard(keyboard=keyboard)


class DateKeyboard(BotKeyboard):
    """
        Клавиатура для указания даты.
        id: 'date_today',
        Кнопки: [date_today].
    """

    def __init__(self):
        super().__init__(keyboard_id='date_today')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("На сегодня", callback_data='date_today'),
        )
        self.set_keyboard(keyboard=keyboard)


class CommitKeyboard(BotKeyboard):
    """
        Клавиатура для подтвеждения.
        id: 'commit',
        Кнопки: [commit].
    """

    def __init__(self):
        super().__init__(keyboard_id='commit')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Подтвердить", callback_data='commit'),
        )
        self.set_keyboard(keyboard=keyboard)


class ReportKeyboard(BotKeyboard):
    """
        Клавиатура для выбора отчета.
        id: 'reports',
        Кнопки: [account_balance, expenses, income].
    """

    def __init__(self):
        super().__init__(keyboard_id='reports')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Остатки", callback_data='account_balance'),
            types.InlineKeyboardButton("Расходы", callback_data='expenses'),
            types.InlineKeyboardButton("Доходы", callback_data='income'),
        )
        self.set_keyboard(keyboard=keyboard)
