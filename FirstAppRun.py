"""Выполняет настройки при первом запуске бота."""
import os.path
from Common import into_int
from Models import Administrator


class OpenFile:
    """Класс для работы с файлами."""

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


def settings_file_exists():
    """Проверяет наличие файла settings.txt"""
    return os.path.isfile('settings.txt')


def dot_env_exists():
    """Проверяет наличие файла .env"""
    return os.path.isfile('.env')


def create_dot_env():
    """Создает файл .env"""
    settings = read_settings_file()
    with OpenFile(filename='.env', mode='w') as f:
        f.write(f"TOKEN = {repr(settings.get('TOKEN'))}")


def create_settings_file():
    """Создает файл settings.txt"""
    with OpenFile(filename='settings.txt', mode='w') as f:
        f.write("TOKEN=\n")
        f.write("ADMIN_NAME=\n")
        f.write("ADMIN_ID=\n")


def read_settings_file() -> dict:
    """Читает файл с настройками и возвращает словарь."""
    keys = ['TOKEN', 'ADMIN_NAME', 'ADMIN_ID']
    with OpenFile(filename='settings.txt', mode='r') as f:
        lines = f.readlines()
    result = {}
    for line in lines:
        if line.find(keys[0]) > -1:
            result.update({keys[0]: line.split('=')[-1].replace('\n', '').strip()})
        elif line.find(keys[1]) > -1:
            result.update({keys[1]: line.split('=')[-1].replace('\n', '').strip()})
        elif line.find(keys[2]) > -1:
            result.update({keys[2]: into_int(line.split('=')[-1].replace('\n', '').strip())})

    return result


def create_admin():
    """Создает в БД пользователя - администратора."""
    settings = read_settings_file()
    new_admin = Administrator()
    new_admin.set_name(user_name=settings.get('ADMIN_NAME'))
    new_admin.set_id(user_id=settings.get('ADMIN_ID'))
    new_admin.validation()
    new_admin.save()


def first_run_procedure():
    """Выполняет необходимые действия при первом запуске бота."""
    if dot_env_exists():
        return

    if not settings_file_exists():
        create_settings_file()
        return

    create_dot_env()
    create_admin()
