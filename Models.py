"""Классы моделей данных."""

from Common import into_float, formatted_sqlite_date_time_now, \
    convert_int_date_time, date_time_is_in_sqlite_format, into_int
from typing import Optional
from NewExeptions import EmptyName
from WorkerDB import get_by_id, get_available_id, insert, update


class Currency:
    """Модель валюты."""
    pass  # TODO: Реализовать класс


class Category:
    """Модель категории затрат."""

    def __init__(self, category_id: Optional[int or str] = None, category_name: Optional[str] = None):
        self.__id = category_id
        self.__name = category_name
        self.__filled_from_db = False

    def set_id(self, category_id: Optional[str or int] = None):
        """
            Устанавливает id категории.
            Если ранее данные были получены из БД, то запрещает изменять id категории.
        """
        if not self.__filled_from_db:
            if category_id is None:
                category_id = self.__get_available_id()
            category_id = into_int(input_value=category_id)
            if category_id is None:
                raise ValueError
            self.__id = category_id

    def set_name(self, category_name: str):
        """Устанавливает имя категории."""
        category_name = category_name.strip()
        if len(category_name) == 0:
            raise EmptyName
        self.__name = category_name

    def get_id(self) -> int:
        """Возвращает id категории."""
        return self.__id

    def get_name(self) -> str:
        """Возвращает имя категории."""
        return self.__name

    def fill_from_db(self, category_id: Optional[int or str] = None):
        """
            Выполняет запрос к БД по id категории.
            Если не передан category_id - использует установленный id, если передан - устанавливает id категории.
            Если существует запись с таким id - заполняет атрибут name.
        """
        self.set_id(category_id=category_id)
        category = get_by_id(
            table_name='categories',
            columns=['id', 'name'],
            id=category_id
        )
        if category_id is not None:
            self.set_name(category_name=category['name'])
            self.__filled_from_db = True

    def save(self):
        """Записывает данные категории в БД или обновляет имя, если ранее данные были получены из БД."""

        if self.get_name() is None:
            raise EmptyName

        if not self.__filled_from_db:
            available_id = self.__get_available_id()
            if self.get_id() is None:
                self.set_id(category_id=available_id)
            elif self.get_id() != available_id:
                self.set_id(category_id=available_id)

            insert(
                table_name='categories',
                column_values=self.__into_dict()
            )
            self.__filled_from_db = True
        else:
            update(
                table_name='categories',
                column_values=self.__into_dict(),
                id=self.get_id()
            )

    def __get_available_id(self) -> int:
        """Возвращает доступный id для новой записи в БД."""
        return get_available_id(table_name='categories')

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'id': self.get_id(),
            'name': self.get_name(),
        }


class Invoice:
    """Модель инвойса."""

    def __init__(self, amount: float or int, currency: Optional[Currency] = None,
                 category: Optional[Category] = None,
                 date_time: Optional[str or int] = None,
                 income=False, expense=False):
        """Конструктор по умолчанию."""
        self.date_time = None
        amount = into_float(amount)
        if amount is None:
            amount = 0.00
        if date_time is None:
            self.date_time = formatted_sqlite_date_time_now()
        elif isinstance(date_time, int):
            self.date_time = convert_int_date_time(date_time=date_time)
        elif isinstance(date_time, str) and date_time_is_in_sqlite_format(date_time=date_time):
            self.date_time = date_time

        self.amount = amount
        self.currency = currency
        self.category = category
        self.income = income
        self.expense = expense
        self.__is_valid = self.__check_valid()
        self.__correct_amount()

    def get_amount(self) -> float:
        """Возвращает сумму инвойса (amount)."""
        return self.amount

    def get_category(self) -> Category or None:
        """Возвращает категорию инвойса (category)."""
        return self.category

    def get_income(self) -> bool:
        """Возвращает признак того, что этот инвойс описывает приход."""
        return self.income

    def get_expense(self) -> bool:
        """Возвращает признак того, что этот инвойс описывает расход."""
        return self.expense

    def get_date_time(self) -> str or None:
        """Возвращает дату инвойса (date_time)."""
        return self.date_time

    def get_currency(self) -> Currency or None:
        """Возвращает валюту."""
        return self.currency

    def is_valid(self) -> bool:
        """Возвращает признак того, что все поля инвойса заполнены верно."""
        return self.__is_valid

    def __check_valid(self) -> bool:
        """Проверяет, верно ли заполнены поля инвойса."""
        if self.get_income() == self.get_expense():
            return False
        if self.get_amount() == 0.00:
            return False
        if self.get_date_time() is None:
            return False
        if self.get_currency() is None:
            return False
        return True

    def __correct_amount(self):
        """Если это расход (expense) - добавляет символ '-' к сумме (amount)."""
        if self.is_valid() and self.get_expense():
            if self.amount > 0.00:
                self.amount *= -1

    def save(self):
        """Сохраняет данные инвойса в БД."""
        if not self.is_valid():
            return  # TODO: Вызывать исключение

        # TODO: column_values для записи в БД должны иметь имена полей таблицы,
        #  а значения - быть типами данных для полей БД.

        # insert(
        #    table_name='cash_flow',
        #    column_values=self.__into_dic()
        # )

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'date_time': self.get_date_time(),
            'amount': self.get_amount(),
            'category': self.get_category(),
            'currency': self.get_currency(),
            'income': self.get_income(),
            'expense': self.get_expense(),
        }
