# derivative and baselines
from typing import OrderedDict
from scipy.spatial import ConvexHull
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.optimize import curve_fit


import pandas as pd
import numpy as np

from .df_transforms import df_trunc


def sd_baseline_correction(
    df, cols=None, freq=0, flip=False, method="min", bounds=[1550, 1750], inplace=False
):
    """ Performs a baseline subtraction on second derivative spectra

    Returns a dataframe of the baseline subtracted data. The dataframe can be
    modified in place, or unmodified with a new dataframe being returned. There
    are two methods for performing the buffer subtraction, a minimum
    value subtraction where zero is set to the smallest value in the defined
    range, or a rubberband method which uses a convexhull approach to baseline
    correction.

    Parameters
    ----------
    df : Dataframe
        pandas dataframe containing the FTIR data. The data must be contain a
        column of the wavenumber data, and a column of the spectral data.

    cols : list (default: None)
        List of column names which define the the absorbance data to be fit.
        These values are column headers, not column indecies. Integer values
        can be used as column names and are thus ambiguous and not allowed for
        defining column indecies.

    freq : Int or Str (default: 0)
        Column index or name for the wavelength data. Defaults to the first
        column in the dataframe, but can be changed to a different index or
        a different name if a different column is used for the wavelength
        column. If an integer is passed, then it is first checked if the
        integer is a column name. If the integer is not a column name, it is
        assumed to be the index of the frequency range.

    method :  Str (default: 'min')
        Method used for baseline subtraction. Can be `min` or `rubberband`.
        `min` subtracts by the minimum value in the defined range. `rubberband`
        applies a convexhull fit of the baseline around the defined range.

    flip : bool (default: False)
        A boolean to flip the data over the x-axis (i.e. muliply by -1)

    bounds : iterable of two numbers (default: [1600, 1700])
        Defines the range to use for baseline subtraction. The default values
        are set around the Amide I band. These values can be expanded to
        include the Amide II or other FTIR features. The max and min value of
        the interable are used

    Returns
    -------
    Dataframe
        Baseline corrected dataframe across the specified range.
    """

    def minimum(spec):
        """ `minimum` value subtraction function applied to the dataframe """
        return spec - spec.min()

    def straight(x, y):
        """ `straight` subtract straight baseline applied to the dataframe """
        bsln = (y[-1] - y[0]) / (x[-1] - x[0]) * (x - x[-1]) + y[-1]
        return y - bsln

    #     def asym_baseline(y):
    #         lam = 10**2.5
    #         p = 0.007
    #         niter = 10
    #         L = len(y)
    #         D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    #         w = np.ones(L)
    #         for i in range(niter):
    #             W = sparse.spdiags(w, 0, L, L)
    #             Z = W + lam * D.dot(D.transpose())
    #             z = spsolve(Z, w * y)
    #             w = p * (y > z) + (1 - p) * (y < z)
    #         return z

    def rubberband(x, y):
        """ `rubberband` subtraction function """
        v = ConvexHull(np.column_stack([x, y])).vertices

        ascending = True if x[0] < x[1] else False

        if ascending:
            # rotate vertices until they start from the lowest one
            v = np.roll(v, -v.argmin())
            v = v[: v.argmax() + 1]
        else:
            # rotate vertices until they start from the highest one
            v = np.roll(v, -v.argmax())
            v = v[: v.argmin() + 1]

        # Create baseline using linear interpolation between vertices
        return y - np.interp(x, x[v], y[v])

    # get the frequency column name
    if freq not in df.columns and isinstance(freq, int):
        # get column name if an integer and not a column header
        freq = df.columns[0]

    # filter around the defined bounds
    if not bounds:
        filtered_df = df
    else:
        filtered_df = df[(df.iloc[:, 0] > min(bounds)) & (df.iloc[:, 0] < max(bounds))]
    if len(filtered_df) == 0:
        raise ValueError(
            "Bounds or frequency column definition returned an " "empty frequeny range"
        )

    # determine which colums to apply corrections
    if not cols:
        cols = [x for x in df.columns if x != freq]

    # flip over the x-axis if needed
    if flip:
        preprocessed_df = filtered_df[cols].apply(lambda x: x * -1)
    else:
        preprocessed_df = filtered_df[cols]

    # apply the baseline subtraction method
    if method == "none":
        corrected_spectra = preprocessed_df

    elif method == "min":
        corrected_spectra = preprocessed_df.apply(minimum)

    elif method == "straight":
        freqCol = filtered_df.iloc[:, 0].values
        vals = dict()
        for colName, colData in preprocessed_df.iteritems():
            vals[colName] = straight(freqCol, colData.values)
        corrected_spectra = pd.DataFrame(data=vals)

    #     elif method == 'asym':
    #         corrected_spectra = preprocessed_df.apply(asym_baseline)

    elif method == "rubberband":
        freqCol = filtered_df.iloc[:, 0].values
        vals = dict()
        for colName, colData in preprocessed_df.iteritems():
            vals[colName] = rubberband(freqCol, colData.values)
        corrected_spectra = pd.DataFrame(data=vals)

    elif method == "complex":
        corrected_spectra = preprocessed_df

    elif method == "LS":
        corrected_spectra = preprocessed_df

    else:
        raise NameError("name {0} is not a supported baseline method" "".format(method))

    # create the final dataframe with a clean index and return
    filtered_df.reset_index(drop=True, inplace=True)
    corrected_spectra.reset_index(drop=True, inplace=True)
    return pd.concat([filtered_df.iloc[:, 0], corrected_spectra], axis=1, sort=False)


def baseline_als(y, lam, niter=10):
    """
    Asymmetric baseline correction algorithm based on
    Paul H. C. Eilers and Hans F.M. Boelens: Baseline Correction with Asymmetric Least Squares Smoothing
    https://stackoverflow.com/questions/29156532/python-baseline-correction-library
    """
    p = 0.0001  # This seems to work in most cases, only varying lam
    L = len(y)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    D = lam * D.dot(
        D.transpose()
    )  # Precompute this term since it does not depend on `w`
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for i in range(niter):
        W.setdiag(w)  # Do not create a new matrix, just update diagonal values
        Z = W + D
        z = spsolve(Z, w * y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z


def lengthen_baseline(x_original, y_original, base_short):
    """
    Applies linear extrapolation to backfill baseline to
    full length from a baseline that was originally
    modulated with the asym_baseline_left_x position
    """
    len_cut = len(y_original) - len(base_short)
    x1 = x_original[(len_cut + 1)]
    x0 = x_original[len_cut]
    lft_m = (base_short[1] - base_short[0]) / (x1 - x0)

    lft_b = base_short[0]

    lft_y_base_cor = lft_m * (x_original[0:len_cut] - x0) + (lft_b)

    #     lft_y_base_cor=-lft_m*(x_original[0:len_cut][::-1]) + lft_b
    return np.concatenate([lft_y_base_cor, base_short])


def apply_als_baseline_to_df(df, asym_baseline_left_x, lam_interval, niter=100):

    x_val = np.asarray(df.iloc[:, 0])

    df_left_x_trunc = df_trunc(df, float(asym_baseline_left_x), x_val[-1])

    # Create a copy of the df, which will have y-values overwritten with fitted baselines
    df_fitted_baseline = df.copy()

    for i in range(len(df.columns) - 1):

        y_val_trunc = np.asarray(df_left_x_trunc.iloc[:, (i + 1)])
        fitted_baseline_trunc = baseline_als(y_val_trunc, lam_interval, niter=100)

        y_val = np.asarray(df.iloc[:, (i + 1)])

        fitted_baseline = lengthen_baseline(x_val, y_val, fitted_baseline_trunc)

        # Overwrite df with baseline-subtracted y data
        df.iloc[:, (i + 1)] = y_val - fitted_baseline

        # Write fitted baseline to df_fitted_baseline
        df_fitted_baseline.iloc[:, (i + 1)] = fitted_baseline

    return df, df_fitted_baseline


"""
Define a function for the baseline function, which directly
follows from the fundamental Rayleigh light scattering
equation, where intensity of scattering is inversely proportional
to the 4th power of wavelength.
Rayleigh, Lord. (1899). XXXIV. On the transmission of light through
an atmosphere containing small particles in suspension, and on the
origin of the blue of the sky. https://doi.org/10.1080/14786449908621276
"""


def ls_uvvis_fun(x, a, b):
    return b / x ** 4 + a


def apply_light_scattering_correction_to_df(df, ref_lambda):

    # Create a copy of the df, which will have y-values overwritten with fitted baselines
    df_fitted_ls_baseline = df.copy()

    # Create a dictionary to hold b param
    b_params = OrderedDict()

    # find the corresponding index location from the wavelength array
    idx = df.iloc[:, 0].sub(ref_lambda).abs().idxmin()  # finds closest index
    # idx = (df[df.iloc[:, 0] == ref_lambda].index.values)[0] # Only works for exact wavelength match

    for i in range(len(df.columns) - 1):
        """
        Create a new x, y array of the baseline region.
        This will form the basis to curve-fit and extrapolate the baseline
        for light scattering baseline correction.
        """

        x, y = df.iloc[idx:, 0].values, df.iloc[idx:, (i + 1)].values
        # curve fit and return the optimized parameters (popt)
        popt, _ = curve_fit(ls_uvvis_fun, x, y)
        # extract the a and b params from popt
        a, b = popt

        b_params[df.columns[i + 1]] = b

        # create the fitted baseline
        y_fit = ls_uvvis_fun(df.iloc[:, 0], a, b)
        # print(df.loc[idx:, 'Wavelength (nm)'].values, df.iloc[idx:, (i+1)].values, np.asarray(y_fit))

        # Overwrite df with baseline-subtracted y data
        df.iloc[:, (i + 1)] = df.iloc[:, (i + 1)].values - np.asarray(y_fit)

        # Write fitted baseline to df_fitted_baseline
        df_fitted_ls_baseline.iloc[:, (i + 1)] = y_fit

    return df, df_fitted_ls_baseline, b_params
