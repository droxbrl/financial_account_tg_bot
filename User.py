"""Модуль пользователей бота."""

from WorkerDB import get_by_id
from Common import into_int


class User:
    """Класс, описывающий модель пользователя."""
    __is_registered: bool

    def __init__(self, user_id: (int, str), user_name: str):

        self.__is_registered = False
        self.__is_valid = False

        self.__id = into_int(user_id)
        if self.__id is None:
            self.__is_valid = True

        if self.__is_valid:
            self.__is_registered = self.__check_registration()
        self.__name = user_name.strip()

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
