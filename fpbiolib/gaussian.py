from .ftir_band_assignments import yang_h20_2015, yang_h20_2015_w_side_chains
import numpy as np
import pandas as pd
import math
from scipy import optimize


def guess_heights(df, col, center_list, gain=0.95):
    """Determines guesses for the heights based on measured data.

    Function creates an integer mapping to the measured frequencies, and then
    creates an initial peak height guess of gain*actual height at x=freq*. A
    Default of 0.95 seems to work best for most spectra, but can be change to
    improve convergence.

    Parameters
    ----------
    df : Dataframe
        Dataframe containing the measured absorbance data

    col : string or integer
        Column index for the absorbance data being fit. Accepts either index
        or string convention.

    center_list : iterable of integers
        An iterable of integer peak positions used to find the experiment
        absorbance at a given wavenumber. I.e, the heights are returned at the
        center values in this iterable

    gain : number (optional)
        Fraction of the measured absorbance value to use determine the initial
        guess for the peak height. The value Default value is 0.95, and thus
        by default, all initial peak guesses are 95% of the peak max.

    """
    heights = []
    freq_map = {}
    for i in df.iloc[:, 0]:
        j = math.floor(i)
        freq_map[j] = float(df[col].get(df.iloc[:, 0] == i))
    for i in center_list:
        height = freq_map[i]
        heights.append(gain * height)
    return heights


def gaussian_least_squares(
    df, col, peaks=yang_h20_2015, peak_width=5, params=dict()
):
    if not col:
        col = df.columns[1]

    def fun(p, x, y):
        """Minimizing across parameter space p, for a given range, x"""
        return gaussian_sum(x, *p) - y

    data = np.array(pd.concat([df.iloc[:, 0], df[col]], axis=1))
    heights = guess_heights(df, col, peaks["means"], gain=1.0)
    width = peak_width
    lb = list()
    ub = list()
    guess = list()

    # Make 1-D array for optimization func definition above
    for mean, bound, height in zip(
        peaks["means"], peaks["uncertainties"], heights
    ):
        lb.extend([0, bound[0], 0])
        ubh = np.inf if height <= 0 else height
        ub.extend([ubh, bound[1], peak_width * 1])
        guess.extend([height * 0.95, mean, peak_width])

    args = [fun, np.array(guess)]
    params["args"] = (data[:, 0], data[:, 1])
    params["bounds"] = (np.array(lb), np.array(ub))
    res = optimize.least_squares(*args, **params)

    areas = list()
    for i in range(0, len(res.x), 3):
        height = res.x[i]
        width = res.x[i + 2]
        area = gaussian_integral(height, width)
        areas.append(area)
    return areas, res


def gaussian(x, height, center, width):
    """Function defining a gaussian distribution"""
    return height * np.exp(-((x - center) ** 2) / (2 * width ** 2))


def gaussian_sum(x, *args):
    """Returns the sum of the gaussian function inputs"""
    return sum(gaussian_list(x, *args))


def gaussian_list(x, *args):
    """Returns the sum of the gaussian function inputs"""
    if len(args) % 3 != 0:
        raise ValueError("Args must divisible by 3")
    gausslist = []
    count = 0
    for i in range(int(len(args) / 3)):
        gausstemp = gaussian(x, args[count], args[count + 1], args[count + 2])
        gausslist.append(gausstemp)
        count += 3

    gausslist = [
        np.where(gausslist[i] < 1.0e-30, 0.0, gausslist[i])
        for i, _ in enumerate(gausslist)
    ]

    # The gaussian peaks resulting from the curve fit often result in values
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero

    return gausslist


def gaussian_integral(height, width):
    """Returns the integral of a gaussian curve with the given height, width
    and center
    """
    return height * width * math.sqrt(2 * math.pi)


def gaussians_to_df(df, gaussian_list_data, fitted_trace):
    tmp_col_names = [
        f"Gaussian {i+1}" for i, _ in enumerate(gaussian_list_data)
    ]
    gaussian_df = pd.DataFrame(gaussian_list_data).transpose()
    gaussian_df.columns = tmp_col_names
    gaussian_df.insert(0, df.columns[0], df.iloc[:, 0])
    gaussian_df.insert(1, fitted_trace, df[fitted_trace])
    gaussian_df.insert(2, "Model Fit", sum(gaussian_list_data))
    return gaussian_df
