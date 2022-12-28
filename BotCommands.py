"""Модуль команд бота."""
from telebot import types
from typing import Optional, List
from Models import all_categories_from_db, all_currencies_from_db


class BotKeyboard:
    """Класс, описывающий команды бота."""

    def __init__(self, keyboard_id: str, keyboard: Optional[types.InlineKeyboardMarkup] = None):
        self.keyboard_id = keyboard_id
        self.keyboard = keyboard

    def set_keyboard(self, keyboard: types.InlineKeyboardMarkup):
        """Устанавливает клавиатуру."""
        self.keyboard = keyboard


class Button:
    """Модель кнопки."""

    def __init__(self, text: str, callback_data: Optional[str] = None):
        self.button = types.InlineKeyboardButton(text, callback_data=callback_data)


class CancelKeyboard(BotKeyboard):
    """
        Клавиатура для отмены действий.
        id: 'cancel',
        Кнопки: [cancel].
    """

    def __init__(self):
        super().__init__(keyboard_id='cancel')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='Отменить', callback_data='cancel'))
        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class StartKeyboard(BotKeyboard):
    """
        Стартовая клавиатура бота.
        id: 'start',
        Кнопки: [add_expenses, add_income, reports].
    """

    def __init__(self):
        super().__init__(keyboard_id='start')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='Внести расход',
                                   callback_data='add_expenses'))
        self.buttons.append(Button(text='Внести доход',
                                   callback_data='add_income'))
        self.buttons.append(Button(text='Отчеты',
                                   callback_data='reports'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class DateKeyboard(BotKeyboard):
    """
        Клавиатура для указания даты.
        id: 'date_today',
        Кнопки: [date_today].
    """

    def __init__(self):
        super().__init__(keyboard_id='date_today')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='На сегодня', callback_data='date_today'))
        self.buttons.append(Button(text='Отменить', callback_data='cancel'))
        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class CommitKeyboard(BotKeyboard):
    """
        Клавиатура для подтвеждения.
        id: 'commit',
        Кнопки: [commit].
    """

    def __init__(self):
        super().__init__(keyboard_id='commit')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='Подтвердить', callback_data='commit'))
        self.buttons.append(Button(text='Отменить', callback_data='cancel'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class ReportsKeyboard(BotKeyboard):
    """
        Клавиатура для выбора отчета.
        id: 'reports',
        Кнопки: [account_balance, expenses, income].
    """

    def __init__(self):
        super().__init__(keyboard_id='reports')
        self.buttons: List[Button] = []
        self.buttons.append(
            Button(text='Остатки', callback_data='account_balance'))
        self.buttons.append(
            Button(text='Расходы', callback_data='expenses'))
        self.buttons.append(
            Button(text='Доходы', callback_data='income'))
        self.buttons.append(
            Button(text='Отменить', callback_data='cancel'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class CategoriesKeyboard(BotKeyboard):
    """
        Клавиатура для выбора категории затрат.
        id: 'categories',
        Кнопки: [category_id_{id}].
    """

    def __init__(self):
        super().__init__(keyboard_id='categories')
        self.buttons: List[Button] = []

        for category in all_categories_from_db():
            self.buttons.append(
                Button(
                    text=category.get_name(),
                    callback_data=f'category_id_{category.get_id()}'
                )
            )
        self.buttons.append(Button(text='Отменить', callback_data='cancel'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class CurrenciesKeyboard(BotKeyboard):
    """
        Клавиатура для выбора валюты.
        id: 'currencies',
        Кнопки: [currency_id_{code}].
    """

    def __init__(self):
        super().__init__(keyboard_id='currencies')
        self.buttons: List[Button] = []

        keyboard = types.InlineKeyboardMarkup()
        for currency in all_currencies_from_db():
            self.buttons.append(
                Button(
                    text=currency.get_code(),
                    callback_data=f'currency_id_{currency.get_code()}'
                )
            )
        self.buttons.append(Button(text='Отменить', callback_data='cancel'))
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)


class YesNoKeyboard(BotKeyboard):
    """
           Клавиатура для ответа на вопрос.
           id: 'group_by_category',
           Кнопки: [group_by_category_yes, group_by_category_no].
    """

    def __init__(self):
        super().__init__(keyboard_id='yes_no')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='Да', callback_data='group_by_category_yes'))
        self.buttons.append(Button(text='Нет', callback_data='group_by_category_no'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button.button)
        self.set_keyboard(keyboard=keyboard)
