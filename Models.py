"""Классы моделей данных."""

from Common import into_float, formatted_sqlite_date_time_now, convert_int_date_time, date_time_is_in_sqlite_format


class Invoice:
    """Класс, описывающий модель инвойса."""

    def __init__(self, amount: float or int, category, date_time=None, income=False, expense=False):
        """Конструктор по умолчанию."""
        self.__date_time = None
        amount = into_float(amount)
        if amount is None:
            amount = 0.00
        if date_time is None:
            self.__date_time = formatted_sqlite_date_time_now()
        elif isinstance(date_time, int):
            self.__date_time = convert_int_date_time(date_time=date_time)
        elif isinstance(date_time, str) and date_time_is_in_sqlite_format(date_time=date_time):
            self.__date_time = date_time
        self.__amount = amount
        self.__category = category
        self.__income = income
        self.__expense = expense
        self.__is_valid = self.__check_valid()
        self.__correct_amount()

    def get_amount(self) -> float:
        """Возвращает сумму инвойса (amount)."""
        return self.__amount

    def get_category(self):
        """Возвращает категорию инвойса (category)."""
        return self.__category

    def get_income(self) -> bool:
        """Возвращает признак того, что этот инвойс описывает приход."""
        return self.__income

    def get_expense(self) -> bool:
        """Возвращает признак того, что этот инвойс описывает расход."""
        return self.__expense

    def get_date_time(self) -> str or None:
        """Возвращает дату инвойса (date_time)."""
        return self.__date_time

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
        return True

    def __correct_amount(self):
        """Если это расход (expense) - добавляет символ '-' к сумме (amount)."""
        if self.is_valid() and self.get_expense():
            if self.__amount > 0.00:
                self.__amount *= -1

    def save(self):
        """Сохраняет данные инвойса в БД."""
        if not self.is_valid():
            return
        # TODO: Реализовать метод

