import math

import numpy as np


def wss(y, y_fit):
    """Work in progress, do not use.  Calculates the Weighted Trace Similarity for two samples"""
    n = int(len(y))
    y_avg = sum(y) / n
    wss_sq = 0
    for i in range(n):
        wss_sq = (
            wss_sq
            + (1 / n) * (abs(y[i]) / abs(y_avg)) * ((y_fit[i]) - (y[i])) ** 2
        )
    wss = 1 - 100 * math.sqrt(wss_sq)
    return wss


def wsd(y, y_fit):
    """Calculates the WSD for two samples"""
    n = int(len(y))
    y_avg = sum(y) / n

    if y_avg != 0:
        wsd_sq = 0
        for i in range(n):
            wsd_sq = (
                wsd_sq
                + (1 / n)
                * (abs(y[i]) / abs(y_avg))
                * ((y_fit[i]) - (y[i])) ** 2
            )
        wsd = math.sqrt(wsd_sq)
    else:
        wsd = 0
    return wsd


def overlap(x, y, y_compare):
    """
    Calculates area of commonality / overlap

    To deal with negative and positive peak areas, we will need
    to take the absolute value of both traces, and then calculate
    the minimum value point-by-point.  We also need to area normalize
    to eliminate errors due to concentration differences. Finally,
    we can automatically assign zero overlap at points where the
    two traces differ in sign.
    """

    # There must be zero overlap if y values have different signs
    # therefore, create an array of 1's and 0's so we can
    # zero out each point in the overlap array later in the algorithm.
    zero_opp_signs = []
    for a, b in zip(y, y_compare):
        if np.sign(a) == np.sign(b):
            zero_opp_signs.append(1)
        else:
            zero_opp_signs.append(0)

    zero_opp_signs = np.asarray(zero_opp_signs)  # create array

    # Make array all positive to facilitate calculation
    # of minimum absolute intensity in point-by-point comparisons
    y_pos = np.abs(y)
    y_compare_pos = np.abs(y_compare)

    # We will need to area normalize both traces.
    # E.g. divide each trace area by the integrated area
    # to create an area of 1.  Then, any area of overlap
    # will be a fractional area.
    y_pos_area = np.abs(np.trapz(y_pos, x))  # need abs to ensure positive area
    y_pos_norm = y_pos / y_pos_area

    # need abs to ensure positive area
    # Avoid division by zero
    if not y_pos_area == 0:
        y_pos_norm = y_pos / y_pos_area
    else:
        y_pos_norm = y_pos_area

    y_compare_pos_area = np.abs(np.trapz(y_compare_pos, x))
    # Avoid division by zero
    if not y_compare_pos_area == 0:
        y_compare_pos_norm = y_compare_pos / y_compare_pos_area
    else:
        y_compare_pos_norm = y_compare_pos_area

    y_min = np.minimum(
        (y_pos_norm), (y_compare_pos_norm)
    )  # finds stepwise minimum element of both datasets

    # Zero out any spots where traces had opposite signs
    y_min = y_min * zero_opp_signs

    y_min_area = np.abs(
        np.trapz(y_min, x)
    )  # get area of y_min, need abs to ensure positive area. Can be negative if wavelength is descending

    return y_min_area


def R2(y, y_compare):
    resid = y - y_compare
    return 1 - np.sum((resid**2)) / np.sum((y - y.mean()) ** 2)


def dca(x, y, y_fit):
    """Calculates the derivative correlation algorithm (DCA) for two samples in the DataFrame"""

    n = int(len(y))
    p_sq = 0
    A = 0
    B = 0
    C = 0
    # create a list of n elements, all zero to make endpoints zero after loop below
    y_der = [0] * n
    y_fit_der = [0] * n

    for i in range(2, n - 1):  # want i = 1 and i = n elements equal to zero
        y_der[i] = (y[i + 1] - y[i - 1]) / 2
        y_fit_der[i] = (y_fit[i + 1] - y_fit[i - 1]) / 2

    for i in range(n):
        A = A + y_der[i] * y_fit_der[i]
        B = B + (y_der[i]) ** 2
        C = C + (y_fit_der[i]) ** 2

    p_sq = A**2 / (B * C)
    p = math.sqrt(p_sq)
    return (p**21 + p) / 2
