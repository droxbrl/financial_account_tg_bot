"""Общие функции."""


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
