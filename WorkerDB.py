"""Модуль для работы с SQLite3."""

import sqlite3
from typing import List, Dict, Optional
from Common import into_int
from Collections import Table


class DataBaseWorker:
    """Класс для подключения и курсора БД SQLite3."""

    def __init__(self, db_path='db.db'):
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()
        self.__query_text = ''

    def set_query_text(self, query_text: str):
        """Устанавливает текст запроса."""
        self.__query_text = query_text

    def get_query_text(self) -> str:
        """Возвращает текст запроса."""
        return self.__query_text

    def execute(self):
        """Выполняет запрос к БД SQLite3."""
        self.cursor.execute(self.get_query_text())

    def executemany(self, values):
        """Выполняет запрос к БД SQLite3."""
        self.cursor.executemany(self.get_query_text(), values)

    def close(self):
        """Закрывает подключение к БД SQLite3."""
        self.clear_query_text()
        self.cursor.close()
        self.connect.close()

    def query_text_is_set(self) -> bool:
        """ Возвращает признак того, установлен ли текст запроса. """
        return len(self.get_query_text()) > 0

    def commit(self):
        """ Коммитит в БД. """
        self.connect.commit()

    def clear_query_text(self):
        """ Очищает текст запроса. """
        self.set_query_text('')


def get_report(report_params: Dict, dbw: [DataBaseWorker] = None) -> Dict or None:
    """
        Возвращает данные о доходах/расходах/остатках исходя из параметров report_params.
    """

    if dbw is None:
        dbw = DataBaseWorker()
    income, expense = 0, 0
    date_start = report_params.get('start_date')
    date_end = report_params.get('end_date')
    account_balance_type = report_params.get('account_balance_type')
    group_by_category = report_params.get('group_by_category', False)

    if report_params.get('expenses_type'):
        income = 0
        expense = 1
    if report_params.get('income_type'):
        income = 1
        expense = 0

    if (not account_balance_type) and (not group_by_category):
        dbw.set_query_text(
            f'SELECT SUM(amount) AS Amount, C.code AS Code FROM cash_flow AS CF '
            f'INNER JOIN currencies AS C ON CF.currency_id = C.id  '
            f'WHERE (CF.date_time BETWEEN {repr(date_start)} AND {repr(date_end)}) '
            f'AND (CF.income = {income} and CF.expense = {expense}) '
            f' GROUP BY Code ')
    elif (not account_balance_type) and group_by_category:
        dbw.set_query_text(
            f'SELECT SUM(CF.amount) AS Amount, Categ.Name AS Category, Curr.code FROM cash_flow CF '
            f'INNER JOIN categories Categ on Categ.id = CF.category_id '
            f'INNER JOIN currencies Curr on CF.currency_id = Curr.id '
            f'WHERE (CF.date_time BETWEEN {repr(date_start)} AND {repr(date_end)}) '
            f'AND CF.expense = {expense} '
            f'GROUP BY Categ.Name, Curr.code '
            f'ORDER BY amount ')
    else:
        '''Отчет об остатках.'''
        dbw.set_query_text(
            f'SELECT SUM(amount) AS Amount, C.code AS Code FROM cash_flow AS CF '
            f'INNER JOIN currencies AS C ON CF.currency_id = C.id '
            f'WHERE CF.date_time <= {repr(date_end)} '
            f' GROUP BY Code ')

    try:
        dbw.execute()
    except sqlite3.OperationalError:
        dbw.close()
        return None
    result = {}
    sql_result = dbw.cursor.fetchall()
    if len(sql_result) == 0:
        return result
    dbw.close()
    for index, column in enumerate(sql_result):
        result[column] = sql_result[index]

    return result


def get_by_id(id: (str, int), table_name: str, columns: List[str], column_id_name='id',
              dbw: Optional[DataBaseWorker] = None) -> Dict or None:
    """
        Возвращает значения полей из таблицы БД по переданному id и списку полей, переданному в columns.
        Если записей нет или возникла ошибка - возвращает None.
    """
    if dbw is None:
        dbw = DataBaseWorker()
    columns_joined = ", ".join(columns)

    if isinstance(id, str):
        query_text = f'SELECT {columns_joined} FROM {table_name} WHERE {column_id_name} = {repr(id)}'
    else:
        query_text = f'SELECT {columns_joined} FROM {table_name} WHERE {column_id_name} = {id}'

    dbw.set_query_text(query_text)
    try:
        dbw.execute()
    except sqlite3.OperationalError:
        dbw.close()
        return None

    sql_result = dbw.cursor.fetchone()
    if sql_result is None:
        return sql_result

    result = {}
    for index, column in enumerate(columns):
        result[column] = sql_result[index]
    dbw.close()
    return result


def get_available_id(table_name: str, column_id_name='id', dbw: Optional[DataBaseWorker] = None) -> int:
    """Возвращает новый id."""
    if dbw is None:
        dbw = DataBaseWorker()
    query_text = f'SELECT max({column_id_name}) FROM {table_name}'
    dbw.set_query_text(query_text)
    try:
        dbw.execute()
    except sqlite3.OperationalError:
        dbw.close()
        return 1
    sql_result = dbw.cursor.fetchone()
    dbw.close()
    if sql_result is None:
        return 1
    available_id = into_int(sql_result[0])
    if available_id is None:
        available_id = 1
    else:
        available_id += 1

    return available_id


def insert(table_name: str, column_values: Dict, dbw: Optional[DataBaseWorker] = None):
    """Записывает данные в БД."""
    if not dbw:
        dbw = DataBaseWorker()
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    query_text = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    dbw.set_query_text(query_text)
    dbw.executemany(values=values)
    dbw.commit()
    dbw.close()


def update(id: (str, int), table_name: str, column_values: Dict, column_id_name='id',
           dbw: Optional[DataBaseWorker] = None):
    """Обновляет данные записей в БД."""
    if not dbw:
        dbw = DataBaseWorker()
    for column in column_values.keys():
        value = column_values[column]
        if isinstance(value, str):
            query_text = f'UPDATE {table_name} SET {column} = {repr(value)} WHERE {column_id_name}={id}'
        else:
            query_text = f'UPDATE {table_name} SET {column} = {value} WHERE {column_id_name}={id}'
        dbw.set_query_text(query_text)
        try:
            dbw.execute()
            dbw.commit()
        except sqlite3.OperationalError:
            dbw.close()
    dbw.close()


def get_all(table_name: str, columns_aliases: Optional[Table] = None,
            dbw: Optional[DataBaseWorker] = None) -> List[Dict] or None:
    """
        Возвращает список словарей всех записей таблицы.
        Если таблица пустая - возвращает пустой список.
        Если возникает ошибка - возвращает None.
    """
    if not dbw:
        dbw = DataBaseWorker()
    if columns_aliases is None:
        columns_aliases = __columns_names(table_name, dbw=dbw)

    select_section = ''
    max_index = columns_aliases.rows.ubound()
    current_row_index = 0
    while current_row_index <= max_index:
        name = columns_aliases.get_value(column='Name', row_index=current_row_index)
        alias = columns_aliases.get_value(column='Alias', row_index=current_row_index)
        current_select_section = f'{name} AS {alias}'
        current_row_index += 1
        if current_row_index <= max_index:
            current_select_section += ', '
        select_section += current_select_section
    sql_text = f'SELECT {select_section} FROM {table_name}'
    dbw.set_query_text(sql_text)
    try:
        dbw.execute()
    except sqlite3.OperationalError:
        dbw.close()
        return None
    sql_result = dbw.cursor.fetchall()
    dbw.close()
    if len(sql_result) == 0:
        return sql_result
    result = []
    for item in sql_result:
        new_dict = {}
        current_row_index = 0
        max_rows_index = columns_aliases.rows.ubound()
        for value in item:
            new_dict.update({columns_aliases.get_value(column='Alias', row_index=current_row_index): value})
            current_row_index += 1
            if max_rows_index < current_row_index:
                break
        result.append(new_dict)
    return result


def __table_info(table_name: str, dbw: Optional[DataBaseWorker] = None) -> List:
    """Возвращает список с информацией о таблице БД."""
    if not dbw:
        dbw = DataBaseWorker()
    sql_text = f'pragma table_info({table_name})'
    dbw.set_query_text(sql_text)
    dbw.execute()
    sql_result = dbw.cursor.fetchall()
    return sql_result


def __columns_names(table_name: str, dbw: Optional[DataBaseWorker] = None) -> Table:
    """Возвращает имена и псевдонимы колонок таблицы."""
    if not dbw:
        dbw = DataBaseWorker()
    table_info = __table_info(table_name=table_name, dbw=dbw)
    result_table = Table(columns=['Name', 'Alias'])
    for column_info in table_info:
        result_table.rows.append(row=[column_info[1], column_info[1]])
    return result_table
