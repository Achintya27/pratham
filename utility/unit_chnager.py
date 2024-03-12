
def unit_change(unit_str):
    """
    Give the multiplier for the values
    :param unit_str: (str) string of the unit
    :return: (float) multiplier
    """
    if len(unit_str) > 1:
        unit_scale = list(unit_str)[0]
        if unit_scale == 'u':
            return 1e-6
        elif unit_scale == 'm':
            return 1e-3
        elif unit_scale == 'n':
            return 1e-9
        elif unit_scale == 'p':
            return 1e-12
        elif unit_scale == 'K':
            return 1e3

    return 1