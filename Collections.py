"""Универсальные коллекции значений."""

from typing import Any, Optional
from NewExeptions import NoSuchColumn, ValuesMoreThanColumns, RowIndexError


class Column:
    """Модель колонки."""

    def __init__(self, name: str):
        self.name = name.capitalize().strip()


class Columns:
    """Модель колонок."""

    def __init__(self, columns_names: list or str or None):
        self.__columns = []
        if isinstance(columns_names, str):
            columns_names = [columns_names]

        if isinstance(columns_names, list):
            for column_name in columns_names:
                self.append(column=column_name)

    def append(self, column: str or Column):
        """Добавляет колонку в коллекцию последним элементом."""
        if isinstance(column, str):
            column = Column(column)
            if column not in self.get_columns():
                self.__columns.append(column)
        elif isinstance(column, Column):
            if column not in self.get_columns():
                self.__columns.append(column)

    def delete(self, column: str or Column or int):
        """Удаляет колонку из коллекции по имени, по экземпляру класса Column или по индексу колонки."""
        if isinstance(column, Column):
            try:
                index = self.get_columns().index(column)
            except ValueError:
                index = None
        elif isinstance(column, str):
            index = self.find(search_column=column)['index']
        elif isinstance(column, int):
            index = column
        else:
            index = None

        if index is not None:
            self.__columns.pop(index)

    def delete_all(self):
        """Удаляет все колонки из коллекции."""
        self.__columns.clear()

    def find(self, search_column: str or Column or int) -> dict:
        """
            Поиск в массиве колонок по имени колонки или по экземпляру класса Column или индексу.
            Возвращает словарь вида ('index': индекс_искомой_колонки,
                                     'column': искомая_колонки(экземпляр класса Column)
                                     'exist': True или False
            Если нет искомой колонки, словарь будет со значениями None, а 'exist' = False.
        """
        search_result = self.__get_search_result()
        if isinstance(search_column, str):
            search_column = search_column.capitalize().strip()
        for index, column in enumerate(self.get_columns()):
            if column == search_column or column.name == search_column:
                search_result['index'] = index
                search_result['column'] = column
                search_result['exist'] = True
                break

        return search_result

    def count(self) -> int:
        """Возвращает количество колонок в коллекции."""
        return len(self.get_columns())

    def ubound(self) -> int:
        """Возвращает максимальный индекс колонки в коллекции."""
        return self.count() - 1

    def get_columns(self) -> list[Column]:
        """Возвращает массив колонок коллекции."""
        return self.__columns

    def set_columns(self, columns: list[str or Column]):
        """
            Очищает колонки и устанавливает уникальные колонки из массива.
            Если после установки колонок, новый массив коллекции пустой, тогда
            устанавливает значения колонок до установки новых.
        """
        current_columns = self.get_columns().copy()
        self.delete_all()
        for column in columns:
            self.append(column=column)
        if self.count() == 0:
            self.set_columns(columns=current_columns)

    def __get_search_result(self) -> dict:
        """Возвращает пустой словарь для хранения результата поиска в коллекции."""
        return {
            'index': None,
            'column': None,
            'exist': False,
        }


class Row:
    """Модель строки."""

    def __init__(self, values: list or None or Any):
        if values is None:
            values = []
        elif not isinstance(values, list):
            values = [values]
        self.values = values

    def delete(self, value: int or Any):
        """Заменяет значение по индексу или значению на None."""
        if isinstance(value, int):
            index = value
        else:
            try:
                index = self.values.index(value)
            except ValueError:
                index = None

        if index is not None:
            self.values[index] = None

    def count(self):
        """Возвращает количество значений в строке."""
        return len(self.values)

    def ubound(self):
        """Возвращает максимальный индекс значений в строке."""
        return self.count() - 1

    def append(self, value: Any):
        """Добавляет значение в строку."""
        self.values.append(value)


class Rows:
    """Модель строк."""

    def __init__(self, rows: list[Row] or None or Any):
        self.__rows = []
        if rows is not None:
            rows = [rows]
            if not isinstance(rows, list):
                rows = [rows]
            for row in rows:
                self.append(row=row)

    def append(self, row: Row or None):
        """Добавляет строку в коллекцию строк."""
        if isinstance(row, Row):
            self.__rows.append(row)
        else:
            self.__rows.append(Row(values=row))

    def delete(self, row: Row or int):
        """Удаляет строку по индексу или экземпляру класса Row."""
        if isinstance(row, Row):
            try:
                index = self.get_rows().index(row)
            except ValueError:
                index = None
        elif isinstance(row, int):
            index = row
        else:
            index = None

        if index is not None:
            self.__rows.pop(index)

    def delete_all(self):
        """Удаляет все строки из коллекции."""
        self.__rows.clear()

    def get_rows(self) -> list[Row]:
        """Возвращает массив строк."""
        return self.__rows

    def get_row(self, index: int) -> Row or None:
        """Возвращает строку или None по индексу."""
        try:
            return self.__rows[index]
        except IndexError:
            return None

    def count(self) -> int:
        """Возвращает количество строк в коллекции."""
        return len(self.get_rows())

    def ubound(self) -> int:
        """Возвращает максимальный индекс строки в коллекции."""
        return self.count() - 1


class Table:
    """Модель таблицы."""

    def __init__(self, columns: Optional[list or str or Columns] = None, rows: Optional[Rows or Any] = None):
        self.rows = Rows(rows=None)
        self.columns = Columns(columns_names=None)
        if not isinstance(rows, Rows):
            rows = Rows(rows=rows)
        if isinstance(columns, Columns):
            self.columns = columns
        else:
            self.columns = Columns(columns_names=columns)

        columns_count = self.columns.count()
        for row in rows.get_rows():
            row_count = row.count()
            if row_count > columns_count:
                raise ValuesMoreThanColumns()

            elif row_count < columns_count:
                difference = columns_count - row_count
                while difference != 0:
                    row.append(value=None)
                    difference -= 1

        self.rows = rows

    class __Cell:
        """ Описывает модель ячейки таблицы."""

        def __init__(self, column: dict, row: Row, value: Any):
            self.column = column
            self.row = row
            self.value = value

        def set_value(self, value: Any):
            """Устанавливает значение в ячейку."""
            index = self.column['index']
            self.row.values[index] = value

    def get_value(self, column: int or Column or str, row_index: int) -> Any:
        """
            Возвращает значение ячейки таблицы по индексу колонки и строки (Row),
            по имени колонки (Column) и индексу строки (Row),
            по колонке (Column) и индексу строки (Row).
            При ошибке поиска ячейки вызывает исключения: NoSuchColumn, RowIndexError
        """

        return self.__find_cell(column=column, row_index=row_index).value

    def set_value(self, value: Any, column: int or Column or str, row_index: int):
        """
            Устанавливает значение value в ячейку таблицы по индексу колонки и строки (Row),
            по имени колонки (Column) и индексу строки (Row),
            по колонке (Column) и индексу строки (Row).
            При ошибке поиска ячейки вызывает исключения: NoSuchColumn, RowIndexError
        """
        cell = self.__find_cell(column=column, row_index=row_index)
        cell.set_value(value=value)

    def get_columns(self) -> Columns:
        """Возвращает коллекцию колонок таблицы."""
        return self.columns

    def get_rows(self) -> Rows:
        """Возвращает коллекцию строк таблицы."""
        return self.rows

    def __find_cell(self, column: int or Column or str, row_index: int) -> __Cell:
        """ Ищет и возвращает ячейку (__Cell) таблицы по индексу колонки и строки (Row),
            по имени колонки (Column) и индексу строки (Row),
            по колонке (Column) и индексу строки (Row).
            При ошибке поиска ячейки вызывает исключения: NoSuchColumn, RowIndexError
        """
        found_column: dict = self.get_columns().find(search_column=column)
        if not found_column['exist']:
            raise NoSuchColumn

        found_row = self.get_rows().get_row(index=row_index)
        if found_row is None:
            raise RowIndexError

        return self.__Cell(column=found_column, row=found_row, value=found_row.values[found_column['index']])


class TreeColumns(Columns):
    """
        Модель колонок дерева значений.
        От родителя отличается обязательным наличем колонок Parent (родитель) и Owner (владелец).
    """

    def __init__(self, columns_names: list or str or None):
        if not isinstance(columns_names, list):
            columns_names = [columns_names]
        columns_names.append('Parent')
        columns_names.append('Owner')
        super().__init__(columns_names)


class TreeRow(Row):
    """
        Модель строки.
        Добавлены обязательные значения колонок Parent (родитель) и Owner (владелец).
        По умолчанию None.
    """

    def __init__(self, values: list or None or Any):
        super().__init__(values)
        self.values.append(None)
        self.values.append(None)


class TreeRows(Rows):
    """Модель дерева значений."""

    def __init__(self, rows: list[Row] or None or Any):
        super().__init__(rows)


class TreeTable(Table):
    """Модель дерева значений."""

    def __init__(self, columns: list or str or None or TreeRows, rows: None or Any or TreeRow):
        super().__init__(columns, rows)

    def get_parent(self, row_index: int) -> Any:
        """ Возвращает значение поля Родитель ячейки по индексу строки. """
        return self.get_value(column='Parent', row_index=row_index)

    def get_owner(self, row_index: int) -> Any:
        """ Возвращает значение поля Владелец ячейки по индексу строки. """
        return self.get_value(column='Owner', row_index=row_index)

    def set_parent(self, parent: Any, row_index: int):
        """Устанавливает значение поля Родитель ячейки по индексу строки."""
        self.set_value(value=parent, column='Parent', row_index=row_index)

    def set_owner(self, owner: Any, row_index: int):
        """Устанавливает значение поля Владелец ячейки по индексу строки."""
        self.set_value(value=owner, column='Owner', row_index=row_index)

