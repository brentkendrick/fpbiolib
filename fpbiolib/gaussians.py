from .ftir_band_assignments import yang_h20_2015, yang_h20_2015_w_side_chains
import numpy as np
import pandas as pd
import math
from scipy import optimize
from .df_transforms import idx_val
import math
from .array_transforms import y_in_x_range, y_fm_x_value


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
        mask = df.iloc[:, 0] == i
        freq_map[j] = float(df.loc[mask, col].values[0])
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
    print("params: ", params)
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
    return height * np.exp(-((x - center) ** 2) / (2 * width**2))


def gaussian_sum(x, *args):
    """Returns the sum of the gaussian function inputs"""
    return sum(all_gaussians(x, *args))


def all_gaussians(x, *args):
    """Returns a list containing all gaussian component peaks passed in by *args"""
    if len(args) % 3 != 0:
        raise ValueError("Args must divisible by 3")
    gaussians = []
    count = 0
    for i in range(int(len(args) / 3)):
        gausstemp = gaussian(x, args[count], args[count + 1], args[count + 2])
        gaussians.append(gausstemp)
        count += 3

    # The gaussian peaks resulting from the curve fit often result in values
    # that are insanely small (e.g. < 1e-30) and should just be converted to zero
    gaussians = [
        np.where(gaussians[i] < 1.0e-30, 0.0, gaussians[i])
        for i, _ in enumerate(gaussians)
    ]

    return gaussians


def gaussian_peaks_p0_and_bounds(
    x,
    y,
    peak_ctrs: list,
    peak_width: float,
    peak_x_uncertainty: float,
    gain=1.0,
):

    lb = []
    ub = []
    p0 = []

    # Make 1-D array for optimization func definition above
    for ctr in peak_ctrs:
        low_x = ctr - peak_x_uncertainty
        high_x = ctr + peak_x_uncertainty
        lb.extend([0, low_x, 0])
        ubh = max(y_in_x_range(x, y, low_x, high_x)) * 1.3
        ub.extend([ubh, high_x, peak_width])
        p0.extend([y_fm_x_value(x, y, ctr) * gain, ctr, peak_width])

    return p0, np.array(lb), np.array(ub)


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


# def y_in_x_range(df, sel_trace, x_range):
#     """Determines guesses for the heights based on measured data.

#     Function creates list of initial peak heights for curve-fitting. A
#     default gain of 1.0 seems to work best for most spectra, but can be changed to
#     improve convergence.

#     Parameters
#     ----------
#     df : Dataframe
#         Dataframe containing the measured absorbance data

#     sel_trace : string or index
#         Column name for the trace data being fit. Accepts either index
#         or string convention.

#     x_range : list
#         beginning and ending (inclusive) 2-D array

#     """
#     return df.loc[idx_val(df, x_range[0]):idx_val(df, x_range[1]), sel_trace]
