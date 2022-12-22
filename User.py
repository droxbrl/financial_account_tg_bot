"""Модуль пользователей бота."""


class User:
    """Класс, описывающий модель пользователя."""
    def __init__(self, id: (int, str), name: str):

        self.__is_registered = False
        self.__is_valid = False

        if isinstance(id, int):
            self.__id = id
        elif isinstance(id, str):
            try:
                self.__id = int(''.join(id.split()))
                self.__is_valid = True
            except ValueError:
                self.__id = None

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

    def is_registered(self) -> bool:
        """Возвращает признак того, зарегистрирован ли пользователь в БД."""
        pass
