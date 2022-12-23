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
                self.__columns.append(Column(column_name))

    def append(self, new_column: str or Column):
        """Добавляет колонку в коллекцию последним элементом."""
        if isinstance(new_column, str):
            self.__columns.append(Column(new_column))
        elif isinstance(new_column, Column):
            self.__columns.append(new_column)

    def delete(self, del_column: str or Column):
        """Удаляет колонку из коллекции."""
        # TODO: Реализовать удаление + удаление по индексу ?
        pass


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
            search_column = search_column.capitalize()
        for index, column in enumerate(self.__columns):
            if column == search_column or column.name == search_column:
                search_result['index'] = index
                search_result['column'] = column
                search_result['exist'] = True
                break

        return search_result

    def count(self) -> int:
        """Возвращает количество колонок в коллекции."""
        return len(self.__columns)

    def ubound(self) -> int:
        """Возвращает максимальный индекс колонки в коллекции."""
        return self.count() - 1

    def __get_search_result(self) -> dict:
        """Возвращает пустой словарь для хранения результата поиска в коллекции."""
        return {
                'index': None,
                'column': None,
                'exist': False,
        }



c_n = ['сумма','Итого']
c_n.append()
columns_collection = Columns(columns_names=c_n)
f = columns_collection.find('итого')
asd=1