"""Модуль команд бота."""
from telebot import types
from typing import Optional, List
from Models import all_categories_from_db, all_currencies_from_db
from Collections import TreeTable, TreeColumns, TreeRow


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

    def __init__(self, text: str, callback_data: Optional[str] = None,
                 owner: Optional[str] = None, parent: Optional[str] = None):
        self.button = types.InlineKeyboardButton(text, callback_data=callback_data)
        self.owner = owner
        self.parent = parent


class StartKeyboard(BotKeyboard):
    """
        Стартовая клавиатура бота.
        id: 'start',
        Кнопки: [add_expenses, add_income, reports].
    """

    def __init__(self):
        super().__init__(keyboard_id='start')
        self.buttons: List[Button] = []
        self.buttons.append(Button(text='Внести расход', callback_data='add_expenses', owner='categories'))
        self.buttons.append(Button(text='Внести доход', callback_data='add_income', owner='currencies'))
        self.buttons.append(Button(text='Отчеты', callback_data='reports', owner='reports'))

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
        self.buttons.append(Button(text='На сегодня', callback_data='date_today', parent='reports'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button)
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
        self.buttons.append(Button(text='Подтвердить', callback_data='commit', parent='# User input'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button)
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
            Button(text='Остатки', callback_data='account_balance', parent='reports', owner='date_today'))
        self.buttons.append(
            Button(text='Расходы', callback_data='expenses', parent='reports', owner='date_today'))
        self.buttons.append(
            Button(text='Доходы', callback_data='income', parent='reports', owner='date_today'))

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button)
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
                    callback_data=f'category_id_{category.get_id()}',
                    parent='add_income',
                    owner='currencies'
                )
            )

        keyboard = types.InlineKeyboardMarkup()
        for button in self.buttons:
            keyboard.add(button)
        self.set_keyboard(keyboard=keyboard)


class CurrenciesKeyboard(BotKeyboard):
    """
        Клавиатура для выбора валюты.
        id: 'currencies',
        Кнопки: [currency_id_{id}].
    """

    def __init__(self):
        super().__init__(keyboard_id='currencies')
        self.buttons: List[Button] = []

        keyboard = types.InlineKeyboardMarkup()
        for currency in all_currencies_from_db():
            self.buttons.append(
                Button(
                    text=currency.get_code(),
                    callback_data=f'currency_id_{currency.get_id()}',
                    parent='categories; add_expenses',
                    owner='# User input'
                )
            )
        for button in self.buttons:
            keyboard.add(button)
        self.set_keyboard(keyboard=keyboard)


def KeyboardMap() -> TreeTable:
    """Возвращает дерево значений, описывающее взаимосвязь команд бота."""
    columns = TreeColumns(columns_names=['id_keyboard', 'id_button'])
    keyboard_map = TreeTable(columns=columns)

    index = 0
    for keyboard in all_keyboards():
        for button in keyboard.buttons:
            row = TreeRow(values=[keyboard.keyboard_id, button.button.callback_data])
            keyboard_map.rows.append(row=row)
            keyboard_map.set_owner(row_index=index, owner=button.owner)
            keyboard_map.set_parent(row_index=index, parent=button.parent)
            index += 1

    return keyboard_map


def all_keyboards() -> List:
    """Возвращает все клавиатуры."""
    return [
        StartKeyboard(),
        DateKeyboard(),
        CommitKeyboard(),
        ReportsKeyboard(),
        CategoriesKeyboard(),
        CurrenciesKeyboard(),
    ]


test = KeyboardMap()