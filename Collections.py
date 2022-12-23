"""Универсальные коллекции значений."""


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

    def find(self, search_column: str or Column) -> dict:
        """
            Поиск в массиве колонок по имени колонки или по экземпляру класса Column.
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
        return self.__columns.copy()

    def set_columns(self, columns: list[str or Column]):
        """ Очищает колонки и устанавливает уникальные колонки из массива.
            Если после установки колонок, новый массив коллекции пустой, тогда
            устанавливает значения колонок до установки новых.
        """
        current_columns = self.get_columns()
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
