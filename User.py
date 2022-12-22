"""Модуль пользователей бота."""

import WorkerDB
from Common import into_int

class User:
    """Класс, описывающий модель пользователя."""

    def __init__(self, id: (int, str), name: str):

        self.__is_registered = False
        self.__is_valid = False

        self.__id = into_int(id)
        if self.__id is None:
            self.__is_valid = True

        if self.__is_valid:
            self.__is_registered = self.__check_registration()
        self.__name = name.strip()

    def get_id(self) -> int:
        """Возвращает id пользователя."""
        return self.__id

    def get_name(self) -> str:
        """Возвразает name (имя) пользователя."""
        return self.__name

    def is_valid(self) -> bool:
        """Возвращает признак, верно ли указана информация пользователя."""
        return self.__is_valid

    def __check_registration(self) -> bool:
        """Проверяет, есть ли пользователь с таким id в БД."""
        if WorkerDB.get_by_id(id=self.__id,
                              column_id_name='user_id',
                              table_name='users',
                              columns=['user_id', 'user_name']) is None:
            return False
        else:
            return True

    def is_registered(self) -> bool:
        """ Возвращает признак того, зарегистрирован ли пользователь. """
        return self.__is_registered
