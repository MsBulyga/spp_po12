def keep(str_val, pattern):
    # Реализация логики согласно спецификации
    if str_val is None or pattern is None:
        raise TypeError("TypeError")

    # Логика: оставляем только те символы из str_val, которые есть в pattern
    return "".join([char for char in str_val if char in pattern])
