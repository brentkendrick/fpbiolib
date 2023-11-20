import math
import numpy as np


def base_roundup(x, base=5):
    """Rounds up to a number that is
    divisible by the base.
    """
    return base * math.ceil(x / base)


def base_rounddown(x, base=5):
    """Rounds up to a number that is
    divisible by the base.
    """
    return base * math.floor(x / base)


def round_up_nearest_order_mag(x):
    if x < 0:
        return -(10 ** (math.ceil(math.log10(abs(x)))))
    else:
        return 10 ** (math.ceil(math.log10(x)))


def round_down_nearest_order_mag(x):
    if x < 0:
        return -(10 ** (math.floor(math.log10(abs(x)))))
    else:
        return 10 ** (math.floor(math.log10(x)))


def interval_range(x_min, x_max):
    """Finds range of evenly spaced
    numbers in the range between
    a min and max value, based on the
    delta. The interval will be such
    that no more than 7 numbers will be
    spaced within the range.
    For example, a range from 0 - 1.2
    would have 7 evenly spaced numbers
    every 0.2 units:
    [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
    """

    abs_delta = abs(x_max - x_min)

    log10_value = math.floor(np.log10(abs_delta))
    norm_delta = abs_delta / 10**log10_value
    if norm_delta <= 1.3:
        interval = 0.2
    elif 1.3 < norm_delta <= 3.5:
        interval = 0.5
    elif 3.5 < norm_delta <= 6.5:
        interval = 1.0
    else:
        interval = 2.0

    interval = interval * 10 ** (log10_value)

    rounded_x_min = base_rounddown(x_min, base=interval)
    rounded_x_max = base_roundup(x_max + interval, base=interval)

    return np.arange(rounded_x_min, rounded_x_max, interval)


def ten_to_the_x(value):
    if type(value) == list:
        valueList = []
        for i in value:
            valueList.append(10**i)
        return valueList
    else:
        return 10**value
