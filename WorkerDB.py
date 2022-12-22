"""Модуль для работы с SQLite3."""

import sqlite3
from typing import List, Dict


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


def get_by_id(id: (str, int), table_name: str, columns: List[str], column_id_name='id', dbw=None) -> Dict or None:
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
