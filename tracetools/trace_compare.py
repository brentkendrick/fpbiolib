import math
import numpy as np


def wss(y, y_fit):
    """Work in progress, do not use.  Calculates the Weighted Trace Similarity for two samples"""
    n = int(len(y))
    y_avg = sum(y) / n
    wss_sq = 0
    for i in range(n):
        wss_sq = (
            wss_sq + (1 / n) * (abs(y[i]) / abs(y_avg)) * ((y_fit[i]) - (y[i])) ** 2
        )
    wss = 1 - 100 * math.sqrt(wss_sq)
    return wss


def wsd(y, y_fit):
    """Calculates the WSD for two samples"""
    n = int(len(y))
    y_avg = sum(y) / n
    wsd_sq = 0
    for i in range(n):
        wsd_sq = (
            wsd_sq + (1 / n) * (abs(y[i]) / abs(y_avg)) * ((y_fit[i]) - (y[i])) ** 2
        )
    wsd = math.sqrt(wsd_sq)
    return wsd


def overlap(x, y, y_comp):
    """Calculates area of commonality / overlap"""

    # first create comparison y data with zeros when y and y_comp differ in signs...there must be zero overlap if y values have different signs
    y_comp_cor_list = []
    for a, b in zip(y, y_comp):
        if np.sign(a) == np.sign(b):
            y_comp_cor_list.append(b)
        else:
            y_comp_cor_list.append(0)

    y_comp_cor = np.asarray(y_comp_cor_list)  # corrected y comparison array

    y_comp_area = np.trapz(y_comp_cor, x)  # integrate area of y comparison array

    if not y_comp_area == 0:
        y_comp_norm = (
            y_comp_cor / y_comp_area
        )  # area normalize to 1  #only include if data can't be normalized externally
    else:
        y_comp_norm = y_comp_area
    y_area = np.trapz(y, x)
    y_area_norm = y / y_area

    y_min = np.minimum(
        (y_area_norm), (y_comp_norm)
    )  # finds stepwise minimum element of both datasets

    y_min_area = np.trapz(y_min, x)  # get area of y_min

    return y_min_area


def R2(y, y_compare):
    resid = y - y_compare
    return 1 - np.sum((resid ** 2)) / np.sum(
        (y - y.mean()) ** 2
    )  # gives R-squared of fit


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

    p_sq = A ** 2 / (B * C)
    p = math.sqrt(p_sq)
    DCA_value = (p ** 21 + p) / 2
    return DCA_value
