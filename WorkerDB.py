"""Модуль для работы с SQLite3."""

import sqlite3
from typing import List, Dict, Optional
from Common import into_int


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
