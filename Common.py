"""Общие функции."""
import datetime


def into_int(input_value: str or int or float) -> int or None:
    """Приводит к типу int, если возникает ошибка ValueError - возвращает None."""
    if isinstance(input_value, int):
        return input_value
    elif isinstance(input_value, float):
        return int(input_value)
    else:
        try:
            result = int(''.join(input_value.split()))
        except ValueError:
            result = None
        except TypeError:
            result = None
        return result


def into_float(input_value: str or int) -> float or None:
    """Приводит к типу float, если возникает ошибка ValueError - возвращает None."""
    if isinstance(input_value, float):
        return input_value
    elif isinstance(input_value, int):
        return float(input_value)
    else:
        try:
            result = float(''.join(input_value.split()).replace(',', '.'))
        except ValueError:
            result = None
        except TypeError:
            result = None
        return result


def into_str_money_format(input_value: str or int or float) -> str:
    """
        Приводит к типу str в формате представления денежных средств, пример:
        10000.00 -> '10 000.00'
        Возвращает тип str.
    """
    if into_int(input_value=input_value) is None:
        return '0.00'
    result_list = ''.join(str(input_value)).replace(',', '.').split('.')
    integer_part = result_list[0]
    integer_part_len = len(integer_part)
    if integer_part_len > 3:
        reversed_integer_part = integer_part[::-1]
        reversed_integer_part_array = []
        count = 0
        for i in reversed_integer_part:
            if count == 3:
                reversed_integer_part_array.append(' ')
                count = 0
            count += 1
            reversed_integer_part_array.append(i)
        integer_part = ''.join(reversed_integer_part_array)[::-1]

    if len(result_list) == 2:
        fractional_part = result_list[1]
        if len(fractional_part) == 1:
            fractional_part += '0'
        elif len(fractional_part) == 0:
            fractional_part += '00'
    else:
        fractional_part = '00'

    return f'{integer_part}.{fractional_part}'


def formatted_sqlite_date_time_now() -> str:
    """
        Возвращает тип str текущую дату и время с точностью до секунд в формате SQLite3.
        Пример: 2022-11-12 15:11:53
    """
    dtn = datetime.datetime.now()
    date = formatted_sqlite_date_now(date=dtn)
    time = formatted_sqlite_time_now(time=dtn)
    return f'{date} {time}'


def formatted_sqlite_date_now(date=None) -> str:
    """Возвращает тип str текущую дату в формате SQLite3."""
    if date is None:
        date = datetime.datetime.now()
    return f'{date.year}-{date.month}-{date.day}'


def formatted_sqlite_time_now(time=None) -> str:
    """Возвращает тип str текущее время с точностью до секунд в формате SQLite3."""
    if time is None:
        time = datetime.datetime.now()
    hour = str(time.hour)
    minute = str(time.minute)
    second = str(time.second)

    if len(hour) < 2:
        hour = '0' + hour
    if len(minute) < 2:
        minute = '0' + minute
    if len(second) < 2:
        second = '0' + second

    return f'{hour}:{minute}:{second}'


def convert_int_date_time(date_time: int) -> str:
    """Преобразует дату в формат %Y-%m-%d %H:%M:%S."""
    return datetime.datetime.fromtimestamp(date_time).strftime('%Y-%m-%d %H:%M:%S')


def date_time_is_in_sqlite_format(date_time: str) -> bool:
    """Проверяет, дата и время в формат SQLite3 или нет."""
    date_time_array = date_time.split(' ')
    try:
        date_array = date_time_array[0].split('-')
    except IndexError:
        return False
    try:
        time_array = date_time_array[1].split(':')
    except IndexError:
        return False

    if len(date_array) != 3:
        return False
    if len(time_array) != 3:
        return False

    return True
