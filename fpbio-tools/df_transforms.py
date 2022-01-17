import numpy as np
import pandas as pd
import peakutils
from scipy.signal import savgol_filter

from .df_cleanup import cleanup_df_import, downcast_floats_and_ints


""" X, MULTI-Y INTERPOLATE """
# Version Jan 4, 2022 B Kendrick
"""
Only interpolate if needed, keep small datasets small
"""
import math
import pandas as pd
import numpy as np


def x_many_y_interpolate(df):

    # if x data is invalid, return empty dataframe
    if df.iloc[:, 0].dtype == object:
        return pd.DataFrame()

    x_min = df.iloc[:, 0].min()
    x_max = df.iloc[:, 0].max()

    """
    To interpolate, need to work within bounds of current dataset
    """

    new_x_start = (
        math.ceil(x_min * 100) / 100
    )  # find nearest high integer, mult then div by 100 to get sig figs we want
    new_x_end = (
        math.floor(x_max * 100) / 100
    )  # mult then div by 100 to get sig figs we want

    """
    Generally, datasets visualized with this app don't need any
    more than 5000 points.
    """
    num_rows = len(df.iloc[:, 0])
    if num_rows > 5000:
        x_new = np.linspace(new_x_start, new_x_end, 5000)
    else:
        x_new = np.linspace(new_x_start, new_x_end, num_rows)

    # Create new dataframe to eventually hold interpolated y data
    proc_df = pd.DataFrame(x_new, columns=["x_data"])

    j = 0
    col_list = df.columns
    x = np.asarray(df.iloc[:, 0].dropna())

    for i in range(int(len(col_list) - 1)):

        # Loop through y-columns and replace with interpolated values based on x_new
        y = np.asarray(df[col_list[j + 1]].dropna())

        if y.dtype != object:

            # If the x, y pairs are differing lengths for some reason, handle it by truncating
            min_size = min(x.size, y.size)
            x = x[:min_size]
            y = y[:min_size]

            y_new = np.interp(
                x_new, x, y
            )  # create new y data by interpolation of x, y to x_new range

            # add to temporary df
            y_series = pd.Series(y_new, name=col_list[j + 1])

            proc_df = pd.concat([proc_df, y_series], axis=1)

        j += 1

    return downcast_floats_and_ints(proc_df)


""" MULTI-X, Y transform """
# Version Jan 4, 2022 B Kendrick
"""
Added logic to test length of dataset and only set to 5000 if needed
otherwise, allow smaller datasets
"""
import math
import pandas as pd
import numpy as np


def many_x_y_to_x_many_y(df):
    x_min = (
        df.iloc[:, ::2].min().min()
    )  # finds the minimum x-value across all x-datasets in df
    x_max = (
        df.iloc[:, ::2].max().max()
    )  # finds the maximum x-value across all x-datasets in df (x lengths vary, need to return max of max)

    new_x_start = (
        math.ceil(x_min * 100) / 100
    )  # find nearest high integer, mult then div by 100 to get sig figs we want
    new_x_end = (
        math.floor(x_max * 100) / 100
    )  # mult then div by 100 to get sig figs we want

    """
    Generally, datasets visualized with this app don't need any
    more than 5000 points.
    """
    num_rows = len(df.iloc[:, 0])
    if num_rows > 5000:
        x_new = np.linspace(new_x_start, new_x_end, 5000)
    else:
        x_new = np.linspace(new_x_start, new_x_end, num_rows)

    # Create new dataframe to eventually hold interpolated y data
    proc_df = pd.DataFrame(x_new, columns=["x_data"])

    j = 0
    col_list = df.columns
    for i in range(int(len(col_list) / 2)):

        # Loop through x-columns 0, 2, 4, ... and replace each with a common spacing
        x = np.asarray(df[col_list[j]].dropna())
        # Loop through y-columns 1, 3, 5, ... and replace with interpolated values based on x_new
        y = np.asarray(df[col_list[j + 1]].dropna())

        if (y.dtype != object) and (x.dtype != object):

            # If the x, y pairs are differing lengths for some reason, handle it by truncating
            min_size = min(x.size, y.size)
            x = x[:min_size]
            y = y[:min_size]

            y_new = np.interp(
                x_new, x, y
            )  # create new y data by interpolation of x, y to x_new range

            # add to temporary df
            y_series = pd.Series(y_new, name=col_list[j + 1])

            proc_df = pd.concat([proc_df, y_series], axis=1)

        j += 2
    return downcast_floats_and_ints(proc_df)


# SHRINK DATASET FOR FASTER VISUALIZATION
# function to take a 1-D array and create x limits to 2nd decimal


def x_reduced(x):
    # We're going to interpolate the data to adjust all cgms to same x-interval, so will need to create a common spacing within the interpolated range
    import math

    desired_x_size = 5000  # number of desired datapoints per column (shorter gives faster processing at expense of resolution)
    cur_x_size = x.size  # current number of datapoints per column
    data_spacing = abs(x[-1] - x[0]) / desired_x_size

    new_x_start = (
        math.ceil(x[0] * 100) / 100
    )  # mult then div by 100 to get sig figs we want
    new_x_end = (
        math.floor(x[-1] * 100) / 100
    )  # mult then div by 100 to get sig figs we want
    return np.arange(new_x_start, new_x_end, data_spacing)  # new x-data spacing/range


def df_reduced(df_r_in):

    # create an empty dict to hold new arrays, create dataframe once size is defined in dict array size
    d = {}
    col_list = df_r_in.columns
    x = np.asarray(df_r_in[col_list[0]].dropna())
    x_new = x_reduced(x)
    d[col_list[0]] = x_new
    for i in range(int(len(col_list) - 1)):
        y = np.asarray(df_r_in[col_list[i + 1]].dropna())
        y_new = np.interp(x_new, x, y)
        #         df.close.rolling(3).mean()
        d[col_list[i + 1]] = y_new

    df_r_out = pd.DataFrame(
        dict([(k, pd.Series(v)) for k, v in d.items()])
    )  # this method deals with arrays of different size

    return df_r_out


def df_trunc(df, left_cut, right_cut):
    idx = pd.IndexSlice

    df_trnc = df.copy()
    filt = (df_trnc.iloc[idx[:, 0]] > left_cut) & (
        df_trnc.iloc[idx[:, 0]] < right_cut
    )  # assign to variable
    return df_trnc.loc[filt]


def df_center(df, df_ctr_pks, thres, min_dist):

    # Find maximum peak center X, and Y values for every data column

    x_val = np.asarray(df_ctr_pks.iloc[:, 0])
    xctrs = []
    yctrs = []

    for i in range(len(df_ctr_pks.columns) - 1):
        y_val = np.asarray(df_ctr_pks.iloc[:, (i + 1)])

        ctr_indexes = peakutils.indexes(y_val, thres, min_dist)
        xctrs.append(x_val[ctr_indexes][0].tolist())
        yctrs.append(y_val[ctr_indexes][0].tolist())

    RTdelta = df.iloc[1, 0] - df.iloc[0, 0]  # retention time data interval

    # Shift the x-axis of the data to align to max peak

    for i in range(len(df.columns) - 2):
        shft = int(
            round((xctrs[i + 1] - xctrs[0]) / RTdelta)
        )  # calculate the integer rows to shift data relative to 1st sample
        df.iloc[:, (i + 2)] = df.iloc[:, (i + 2)].shift(-shft)

    # Fill in ends of data after dataframe shift
    df.ffill(axis=0, inplace=True)
    df.bfill(axis=0, inplace=True)
    return df


def find_deriv(df, flip, window_length=5):
    """Adds the 2nd derivative of the chosen signal to the DataFrame
        Window_length=5 is recommended from our studies"""

    proteins = list(df.columns)[1:]

    for i in proteins:

        if flip:
            # negative if want flipped
            dd = -1 * savgol_filter(
                df[i], deriv=2, window_length=window_length, polyorder=3
            )
        else:
            dd = savgol_filter(df[i], deriv=2, window_length=window_length, polyorder=3)

        df[i] = dd

    return df


def df_area_norm(df):
    """Normalize to area of 1 to give intuitive feel for peak area fraction"""
    df.reset_index(drop=True, inplace=True)

    proteins = list(df.columns)[1:]

    for i in proteins:
        dy = np.trapz(abs(df[i]), df[df.columns[0]])
        df[i] = df[i] / abs(
            dy
        )  # absolute value because decreasing x-values give negative area

    return df


def df_min_max_norm(df):
    # df.iloc[:, 1:] = df.iloc[:, 1:].apply(lambda x: (x-x.mean())/ x.std(), axis=0)  # This is a std way of normalizing where you simply subtract the mean and divide by standard deviation.
    df.iloc[:, 1:] = (df.iloc[:, 1:] - df.iloc[:, 1:].min()) / (
        df.iloc[:, 1:].max() - df.iloc[:, 1:].min()
    )  # This is a true min max normalization
    return df
