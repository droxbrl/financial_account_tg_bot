"""Классы моделей данных."""
from Common import into_int, into_float, formatted_sqlite_date_time_now, \
    convert_int_date_time, date_time_is_in_sqlite_format, \
    into_sqlite_date_format, into_date_format
from typing import Optional, Dict, List
from NewExeptions import EmptyName, EmptyCode, InvalidInvoice, InvalidCurrencyCode, InvalidUserData
from WorkerDB import insert, update, \
    get_by_id, get_available_id, get_all, get_report


class User:
    """Класс, описывающий модель пользователя."""

    def __init__(self, user_id: (int or str), user_name: str):

        self.__is_registered = False
        self.__is_valid = False

        self.__id = into_int(user_id)
        if self.__id is not None:
            self.__is_valid = True

        if self.__is_valid:
            self.__is_registered = self.__check_registration()
            try:
                user_name = user_name.strip()
            except TypeError:
                user_name = ''
        self.__name = user_name

    def get_id(self) -> int:
        """Возвращает id пользователя."""
        return self.__id

    def get_name(self) -> str:
        """Возвращает name (имя) пользователя."""
        return self.__name

    def is_valid(self) -> bool:
        """Возвращает признак, верно ли заполнены поля пользователя."""
        return self.__is_valid

    def __check_registration(self) -> bool:
        """Проверяет, есть ли пользователь с таким id в БД."""
        if get_by_id(
                id=self.get_id(),
                column_id_name='user_id',
                table_name='users',
                columns=['user_id', 'user_name']
        ) is None:
            return False
        else:
            return True

    def is_registered(self) -> bool:
        """ Возвращает признак того, зарегистрирован ли пользователь. """
        return self.__is_registered

    def save(self):
        """Записывает пользователя БД."""
        if not self.is_valid():
            raise InvalidUserData
        if self.is_registered():
            return

        insert(table_name='users',
               column_values=self.__into_dict()
               )

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'user_id': self.get_id(),
            'user_name': self.get_name(),
            'user_is_admin': 0,
        }


class Administrator(User):
    """Модель администратора."""

    def __init__(self):
        admin = self.fill_from_db()
        if admin is None:
            super().__init__(user_id=None, user_name='')
        else:
            super().__init__(user_id=admin['user_id'], user_name=admin['user_name'])
        self.__is_admin = 1

    def save(self):
        """Записывает администратора в БД."""
        if not self.is_valid():
            raise InvalidUserData
        if self.is_registered():
            update(
                table_name='users',
                column_values=self.__into_dict(),
                id=self.get_id(),
                column_id_name='user_id'
            )
        else:
            insert(table_name='users',
                   column_values=self.__into_dict()
                   )

    @staticmethod
    def fill_from_db() -> dict or None:
        """Получает данные из БД для атрибутов класса."""
        return get_by_id(
            table_name='users',
            columns=['user_id', 'user_name', 'user_is_admin'],
            id=1,
            column_id_name='user_is_admin'
        )

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'user_id': self.get_id(),
            'user_name': self.get_name(),
            'user_is_admin': self.__is_admin,
        }


class Currency:
    """Модель валюты."""

    def __init__(self, currency_code: Optional[str] = None, currency_id: Optional[int or str] = None):
        if isinstance(currency_code, str):
            currency_code = currency_code.strip().upper()
        self.__code = currency_code
        if isinstance(currency_id, str) or isinstance(currency_id, int):
            currency_id = into_int(currency_id)
        self.__id = currency_id
        self.__filled_from_db = False

    @classmethod
    def cnstr_dict(cls, dict_data: Dict, filled_from_db: Optional[bool] = False):
        """
            Конструктор класса по словарю (dict_data).
            В словаре должны быть ключи: 'code', 'id'.
            По ключу 'code' должно быть значение.
            Параметр 'filled_from_db' - опциональный - см. метод __set_filled_from_db.
        """
        if not isinstance(dict_data, Dict):
            return None
        if 'code' not in dict_data.keys() or 'id' not in dict_data.keys():
            return None
        currency_code = dict_data.get('code')
        if not currency_code:
            return None
        cls_example = cls(
            currency_id=dict_data.get('id'),
            currency_code=currency_code
        )
        cls_example.__set_filled_from_db(filled_from_db=filled_from_db)
        return cls_example

    def set_code(self, currency_code: str):
        """
            Устанавливает код (code) валюты.
            Если ранее данные были получены из БД, то запрещает изменять код валюты.
        """
        if not self.__filled_from_db:
            self.__code = currency_code.strip().upper()

    def set_id(self, currency_id: Optional[int or str] = None):
        """
            Устанавливает переданный id валюты если он равен новому доступному,
            если нет - устанавливает новый доступный id.
        """
        available_id = self.__get_available_id()
        if currency_id is None:
            currency_id = self.__get_available_id()
        currency_id = into_int(input_value=currency_id)
        if currency_id is None:
            raise ValueError
        if currency_id != available_id:
            currency_id = available_id
        self.__id = currency_id

    def get_code(self) -> str or None:
        """Возвращает код (code) валюты."""
        return self.__code

    def get_id(self) -> int or None:
        """Возвращает id валюты."""
        return self.__id

    def fill_from_db(self, currency_code: Optional[str] = None):
        """
            Выполняет запрос к БД по коду (code) валюты.
            Если не передан category_id - использует установленный код (code),
            если передан - устанавливает код (code) валюты.
            Если существует запись с таким кодом (code) - заполняет атрибут id.
        """
        if currency_code is None:
            currency_code = self.__code
        self.set_code(currency_code=currency_code)
        currency = get_by_id(
            table_name='currencies',
            columns=['code', 'id'],
            id=self.get_code(),
            column_id_name='code'
        )

        if currency is not None:
            self.__id = currency['id']
            self.__set_filled_from_db(filled_from_db=True)

    def save(self):
        """Записывает данные валюты в БД."""
        if not self.get_code():
            raise EmptyCode
        if len(self.get_code()) > 3:
            raise InvalidCurrencyCode
        if not self.__filled_from_db:
            self.set_id()

        insert(table_name='currencies',
               column_values=self.__into_dict()
               )

    @staticmethod
    def __get_available_id() -> int:
        """Возвращает доступный id для новой записи в БД."""
        return get_available_id(table_name='currencies')

    def __set_filled_from_db(self, filled_from_db: bool):
        """Устанавливает признак того, получены ли данные валюты из БД."""
        self.__filled_from_db = filled_from_db

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'code': self.get_code(),
            'id': self.get_id(),
        }


class Category:
    """Модель категории затрат."""

    def __init__(self, category_id: Optional[int or str] = None, category_name: Optional[str] = None):
        self.__id = category_id
        self.__name = category_name
        self.__filled_from_db = False

    @classmethod
    def cnstr_dict(cls, dict_data: Dict, filled_from_db: Optional[bool] = False):
        """
            Конструктор класса по словарю (dict_data).
            В словаре должны быть ключи: 'id', 'name'.
            По ключу 'name' должно быть значение.
            Параметр 'filled_from_db' - опциональный - см. метод __set_filled_from_db.
        """
        if not isinstance(dict_data, Dict):
            return None
        if 'id' not in dict_data.keys() or 'name' not in dict_data.keys():
            return None

        cls_example = cls(
            category_id=dict_data.get('id'),
            category_name=dict_data.get('name')
        )
        cls_example.__set_filled_from_db(filled_from_db=filled_from_db)
        return cls_example

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
        if category is not None:
            self.set_name(category_name=category['name'])
            self.__set_filled_from_db(filled_from_db=True)

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
            self.__set_filled_from_db(filled_from_db=True)
        else:
            update(
                table_name='categories',
                column_values=self.__into_dict(),
                id=self.get_id()
            )

    @staticmethod
    def __get_available_id() -> int:
        """Возвращает доступный id для новой записи в БД."""
        return get_available_id(table_name='categories')

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        return {
            'id': self.get_id(),
            'name': self.get_name(),
        }

    def __set_filled_from_db(self, filled_from_db: bool):
        """Устанавливает признак того, получены ли данные категории из БД."""
        self.__filled_from_db = filled_from_db


class Invoice:
    """Модель инвойса."""

    def __init__(self, amount: Optional[float or int] = None, currency: Optional[Currency] = None,
                 category: Optional[Category] = None,
                 date_time: Optional[str or int] = None,
                 user: Optional[User] = None,
                 income=False, expense=False):
        """Конструктор по умолчанию."""
        self.date_time = None
        if amount is None:
            amount = 0.00
        if date_time is None:
            self.date_time = formatted_sqlite_date_time_now()
        elif isinstance(date_time, int):
            self.date_time = convert_int_date_time(date_time=date_time)
        elif isinstance(date_time, str) and date_time_is_in_sqlite_format(date_time=date_time):
            self.date_time = date_time

        self.amount = into_float(amount)
        self.currency = currency
        self.category = category
        self.income = income
        self.expense = expense
        self.__is_valid = self.__check_valid()
        self.__correct_amount()
        self.user = user

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
        self.__is_valid = self.__check_valid()
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

    def set_amount(self, amount: int or float or str):
        """Устанавливает сумму."""
        amount = into_float(amount)
        if amount is None:
            amount = 0.00
        self.amount = amount
        self.__correct_amount()

    def save(self):
        """Сохраняет данные инвойса в БД."""
        if not self.is_valid():
            raise InvalidInvoice

        insert(
            table_name='cash_flow',
            column_values=self.__into_dict()
        )

    def __into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        if self.get_category() is None:
            category_id = ''
        else:
            category_id = self.get_category().get_id()

        if self.user is None:
            user_id = 0
        else:
            user_id = self.user.get_id()

        return {
            'date_time': self.get_date_time(),
            'amount': self.get_amount(),
            'category_id': category_id,
            'currency_id': self.get_currency().get_id(),
            'income': self.get_income(),
            'expense': self.get_expense(),
            'user_id': user_id
        }

    def __str__(self):

        if self.expense:
            symbol = ''
        else:
            symbol = '+'

        if self.category is None:
            str_cat = ''
        else:
            str_cat = 'в категории ' + repr(self.category.get_name())

        if self.currency is None:
            str_cur = ''
        else:
            str_cur = self.currency.get_code()

        return f'{symbol} {self.amount} {str_cur} {str_cat}'


class Report:
    """Модель отчета."""

    def __init__(self, account_balance=False, expenses=False, income=False,
                 period: Optional[str] = None, group_by_category: Optional[bool] = False):
        self.report_types = dict(account_balance=account_balance, expenses=expenses, income=income)
        self.period = self.parse_period(report_period=period)
        self.__report_data = None
        self.group_by_category = group_by_category

    def __str__(self):
        if self.__report_data is None:
            return 'Нет данных'
        if self.report_types.get('account_balance'):
            smthg = 'На ' + self.end_date
            rep_type = 'остатки'
        else:
            smthg = 'За ' + self.start_date + '-' + self.end_date
            if self.report_types.get('expenses'):
                rep_type = 'расходы'
            else:
                rep_type = 'доходы'
        rep_data = ''
        for item in self.__report_data:
            if len(item) == 2:
                curr_data = f'{item[0]} {item[1]}'
            elif len(item) == 3:
                curr_data = f'{item[0]} {item[2]} > {item[1]}'
            else:
                curr_data = ''
            rep_data += curr_data + '\n'
        text = f'{smthg} у Вас следующие {rep_type}: \n' \
               f'{rep_data}'
        return text

    @staticmethod
    def parse_period(report_period: Optional[str] = None, sep: Optional[str] = '-') -> Dict:
        """Парсит период, определяет даты начала и конца."""
        start_date = formatted_sqlite_date_time_now(start_of_the_day=True)
        end_date = formatted_sqlite_date_time_now(end_of_the_day=True)
        if report_period is not None:
            date_list = report_period.strip().split(sep)
            if len(date_list) == 2:
                start_date = into_sqlite_date_format(date=date_list[0]) + ' 00:00:00'
                end_date = into_sqlite_date_format(date=date_list[1]) + ' 23:59:59'
        return dict(start=start_date, end=end_date)

    @property
    def start_date(self) -> str:
        """Дата и время начала отчета."""
        start_date = self.period.get('start')
        return into_date_format(date=start_date, no_time_income_date=False)

    @property
    def end_date(self) -> str:
        """Дата и время конца отчета."""
        end_date = self.period.get('end')
        return into_date_format(date=end_date, no_time_income_date=False)

    @start_date.setter
    def start_date(self, start_date: str):
        """
            Устанавливает дату начала.
            Если start_date не передан - установит текущую дату и время начала дня.
        """
        if start_date is not None:
            if start_date.find('-') < 0:
                start_date += '-'
        parsed = self.parse_period(start_date)
        self.period.update({'start': parsed.get('start')})

    @end_date.setter
    def end_date(self, end_date: str):
        """
            Устанавливает дату конца.
            Если end_date не передан - установит текущую дату и время конца дня.
        """
        if end_date is not None:
            if end_date.find('-') < 0:
                end_date = '-' + end_date
        parsed = self.parse_period(end_date)
        self.period.update({'end': parsed.get('end')})

    def set_report_type(self,
                        account_balance: Optional[bool] = None,
                        expenses: Optional[bool] = None,
                        income: Optional[bool] = None):
        """
            Устанавливает тип отчета.
        """
        if isinstance(account_balance, bool):
            self.report_types.update({'account_balance': account_balance})
        if isinstance(expenses, bool):
            self.report_types.update({'expenses': expenses})
        if isinstance(income, bool):
            self.report_types.update({'income': income})

    def fill_report_data_from_db(self):
        """Получает данные отчета из БД."""
        if self.__report_data is None:
            params = self.__params_into_dict()
            self.__report_data = get_report(report_params=params)

    def __params_into_dict(self):
        """Возвращает словарь где ключи - имена атрибутов класса, а значения - значения атрибутов класса."""
        account_balance_type = self.report_types.get('account_balance')
        expenses_type = self.report_types.get('expenses')
        income_type = self.report_types.get('income')
        return {
            'start_date': self.period.get('start'),
            'end_date': self.period.get('end'),
            'account_balance_type': account_balance_type,
            'expenses_type': expenses_type,
            'income_type': income_type,
            'group_by_category': self.group_by_category,
        }


class Stack:
    """Стак созданных в процессе работы бота инвойсов и отчетов."""

    def __init__(self):
        self.__data = {}

    def add_user(self, user: User, invoice: Optional[Invoice] = None, report: Optional[Report] = None):
        """Добавляет пользователя в стак."""
        for added_user in self.__data.keys():
            if added_user.get_id() == user.get_id():
                return

        self.__data.update(
            {
                user: {
                    'invoice': invoice,
                    'report': report
                }
            }
        )

    def add_invoice(self, user: User, invoice: Invoice):
        """Добавляет данные инвойса в стак."""
        data = self.__data.get(user)
        if data is not None:
            data.update({'invoice': invoice})
            self.__data.update({user: data})

    def add_report(self, user: User, report: Report):
        """Добавляет данные отчета в стак."""
        data = self.__data.get(user)
        if data is not None:
            data.update({'report': report})
            self.__data.update({user: data})

    def get_invoice_by_user(self, user: User) -> Invoice or None:
        """Возвращает инвойс по переданному пользователю или None."""
        data = self.__data.get(user)
        return data.get('invoice')

    def get_report_by_user(self, user: User) -> Report or None:
        """Возвращает отчет по переданному пользователю или None."""
        data = self.__data.get(user)
        return data.get('report')

    def get_users(self) -> List[User] or None:
        """Возвращает список все пользователей из стака."""
        result = []
        for user in self.__data.keys():
            result.append(user)
        if len(result) == 0:
            return None
        return result

    def get_user_by_id(self, user_id: str or int) -> User or None:
        """Возвращает пользователя по id или None."""
        user_id = into_int(user_id)
        if user_id is None:
            return None
        users = self.get_users()
        if users is None:
            return None
        for user in users:
            if user.get_id() == user_id:
                return user
        return None

    def clear_all(self):
        """Очищает стак."""
        self.__data.clear()

    def clear_by_user(self, user: User):
        """Удаляет пользователя из стака."""
        try:
            self.__data.pop(user)
        except KeyError:
            pass


def all_categories_from_db() -> List[Category]:
    """Возвращает список всех категорий из БД или пустой список, если нет записей в таблице."""
    categories = get_all(table_name='categories')
    result = []
    if categories is None:
        return result
    elif len(categories) == 0:
        return result

    for category in categories:
        result.append(Category.cnstr_dict(dict_data=category, filled_from_db=True))
    return result


def all_currencies_from_db() -> List[Currency]:
    """Возвращает список всех валют из БД или пустой список, если нет записей в таблице."""
    currencies = get_all(table_name='currencies')
    result = []
    if currencies is None:
        return result
    elif len(currencies) == 0:
        return result

    for currency in currencies:
        result.append(Currency.cnstr_dict(dict_data=currency, filled_from_db=True))
    return result
