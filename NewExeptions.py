""" Дополнительные исключения. """


class ValuesMoreThanColumns(Exception):
    """Исключение возникает, если в таблицу (Table) передано значений (Rows) больше чем колонок (Columns)."""

    def __init__(self):
        self.txt = 'There are more rows than columns in the table!'


class NoSuchColumn(Exception):
    """Исключение возникает, если в таблице (Table) нет искомой колонки (Column)."""

    def __init__(self):
        self.text = 'There is no such column in the table!'


class RowIndexError(IndexError):
    """Исключение возникает, если в таблице (Table) нет искомой строки (Row)."""

    def __init__(self):
        self.text = 'There is no such row in the table!'


class EmptyName(Exception):
    """Исключение возникает, когда установили атрибуту name значение равное пустой строке."""

    def __init__(self):
        self.text = 'Name cannot be empty string!'


class EmptyCode(Exception):
    """Исключение возникает, когда установили атрибуту code значение равное пустой строке."""

    def __init__(self):
        self.text = 'Code cannot be empty string!'
