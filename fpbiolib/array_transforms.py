import numpy as np


def idx_fm_value(x, x_value):
    """Obtains index of x_value from
    array x
    """
    return np.abs(x - x_value).argmin()


def y_fm_x_value(x, y, x_value):
    """Obtains y value from index of
    x_valye
    """
    idx = idx_fm_value(x, x_value)
    return y[idx]


def y_in_x_range(x, y, min_x, max_x):
    """Truncate y array values based on complimentary
    x array values"""
    y_trunc = y[(x >= min_x) & (x <= max_x)]
    return y_trunc
