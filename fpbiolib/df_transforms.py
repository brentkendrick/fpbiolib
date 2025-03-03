import math
import uuid

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

from .df_cleanup import downcast_floats_and_ints, rename_dup_cols_in_two_dfs


def find_idxs_of_str_in_dataframe(df: pd.DataFrame, search_str: str):
    """Returns an array of arrays with cell coordinates
    within the entire dataframe containing the full string.
    """
    return np.argwhere(df.values.astype(f"str") == search_str)


def promote_first_row_to_header(df):
    df.columns = df.iloc[0].to_list()
    df.columns = [str(x) for x in df.columns]
    df = df[1:]
    return df.reset_index(drop=True)


def idx_val(df, val):
    """
    In an x, mult-y dataframe, returns the index for the
    column 0 value closest to the value passed.
    """
    return df.iloc[:, 0].sub(val).abs().idxmin()


def y_in_df_x_range(df, sel_trace, min_x, max_x):
    """Truncate a dataframe's x (index 0) and
    y (specified column name) values and return
    y array"""
    x = df[df.columns[0]]
    y = df[sel_trace]
    y_trunc = y[(x >= min_x) & (x <= max_x)].values
    return y_trunc


def x_y_in_df_x_range(df: pd.DataFrame, sel_trace: str, min_x: float, max_x: float):
    """Truncate a dataframe's x (index 0) and
    y (specified column name) values and return
    x and y arrays"""
    x = df[df.columns[0]]
    y = df[sel_trace]
    x_trunc = x[(x >= min_x) & (x <= max_x)].values
    y_trunc = y[(x >= min_x) & (x <= max_x)].values
    return x_trunc, y_trunc


def log_df(df):
    """Convert x, y arrays in df to log arrays"""
    log_df = pd.DataFrame()
    for column in df.columns[1:]:
        # Can't take the log of zero or a negative number (one limitation
        # of this methodology.  Therefore baseline correct to minimum value.
        y = df[column].values
        y_cor = y - y.min()
        # To avoid -inf values in the array, replace with zeros
        # Still get a divide by zero warning, but it works...
        log_df[column] = np.where(y_cor > 0, np.log10(y_cor), 0)

    log_df.insert(0, df.columns[0], np.log10(df.iloc[:, 0].values))
    return log_df


# When combining x_many_y datasets together, first create a temp
# many_x_y, concat them, and then run them through many_x_y_to_x_many_y
def x_many_y_to_many_x_y(df):
    i = 2
    for _ in range(len(df.columns) - 2):
        unique_id = str(uuid.uuid4())
        df.insert(i, f"x-tmp-{unique_id}", df.iloc[:, 0].to_numpy())
        i += 2
    return df


def x_many_y_interpolate(df, cap=True):
    """
    Interpolates to consistent length. cap is used when
    datasets visualized with this app don't need any
    more than 5000 points.
    """
    # if x data is invalid, return empty dataframe
    if df.iloc[:, 0].dtype == object:
        return pd.DataFrame()

    x_min = df.iloc[:, 0].min()
    x_max = df.iloc[:, 0].max()

    new_x_start = (
        math.ceil(x_min * 100) / 100
    )  # find nearest high integer, mult then div by 100 to get sig figs we want
    new_x_end = (
        math.floor(x_max * 100) / 100
    )  # mult then div by 100 to get sig figs we want

    num_rows = len(df.iloc[:, 0])
    if num_rows > 5000 and cap is True:
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


def many_x_y_to_x_many_y(df, cap=True, new_x=True, num_rows=None, x_data=[]):
    """
    Generally, datasets visualized with this app don't need any
    more than 5000 points.
    """
    x_min = (
        df.iloc[:, ::2].min().min()
    )  # finds the minimum x-value across all x-datasets in df
    x_max = (
        df.iloc[:, ::2].max().max()
    )  # finds the maximum x-value across all x-datasets in df (x lengths vary, need to return max of max)

    # Nice round numbers for plotly tools, otherwise not necessary
    if new_x:
        new_x_start = (
            math.ceil(x_min * 100) / 100
        )  # find nearest high integer, mult then div by 100 to get sig figs we want
        new_x_end = (
            math.floor(x_max * 100) / 100
        )  # mult then div by 100 to get sig figs we want
    else:
        new_x_start = x_min
        new_x_end = x_max

    if not num_rows:
        num_rows = len(df.iloc[:, 0])
        
    if num_rows > 5000 and cap is True:
        x_new = np.linspace(new_x_start, new_x_end, 5000)
    else:
        x_new = np.linspace(new_x_start, new_x_end, num_rows)
    
    if x_data.any():
        x_new = x_data
        new_x_start = x_data.min()
        new_x_end = x_data.max()

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


def many_x_y_to_x_many_y_no_interpolate(df):
    # Create new dataframe to hold y data
    proc_df = pd.DataFrame(df.iloc[:, 0]).copy()

    j = 0
    for i in range(int(len(df.columns) / 2)):
        # Loop through y-columns 1, 3, 5, ... and replace with interpolated values based on x_new
        y = df.iloc[:, j + 1]

        # add to temporary df

        proc_df = pd.concat([proc_df, y], axis=1)
        j += 2

    # print("proc_df: \n", proc_df)
    return downcast_floats_and_ints(proc_df)


def x_reduced(x):
    """SHRINK DATASET FOR FASTER VISUALIZATION
    function to take a 1-D array and create x limits to 2nd decimal
    We're going to interpolate the data to adjust all cgms to same x-interval, so will need to create a common spacing within the interpolated range
    """

    desired_x_size = 5000  # smaller gives faster processing at expense of resolution)
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
    filt = (df.iloc[:, 0] >= left_cut) & (df.iloc[:, 0] <= right_cut)
    return df.loc[filt]


def df_center(df, df_ctr_pks, thres, reference_trace):
    # Find maximum peak center X, and Y values for every data column

    x_val = df_ctr_pks.iloc[:, 0].values
    xctrs = []

    for i in range(len(df_ctr_pks.columns) - 1):
        y_val = np.asarray(df_ctr_pks.iloc[:, (i + 1)])

        ctr_indexes, _ = find_peaks(y_val, prominence=thres)
        if ctr_indexes.size == 0:
            return df
        else:
            xctrs.append(x_val[ctr_indexes][0].tolist())

    # print("reference trace: ", reference_trace)
    # print("X centers: ", xctrs)

    x_interval = df.iloc[1, 0] - df.iloc[0, 0]  # x-data interval

    # Shift the x-axis of the data to align to max peak of reference

    # Get index of reference column in df, which will be related to the index
    # in the xctrs array by a factor of -1 (no x column in the xctrs array)
    # then shift each y-data column by the appropriate factor
    ref_idx = df.columns.get_loc(reference_trace) - 1

    # print("ref_idx: ", ref_idx)
    for i in range(len(df.columns) - 1):
        shft = int(
            round((xctrs[i] - xctrs[ref_idx]) / x_interval)
        )  # calculate the integer rows to shift data relative to 1st sample
        df.iloc[:, (i + 1)] = df.iloc[:, (i + 1)].shift(-shft)

    # Fill in ends of data after dataframe shift
    df.ffill(axis=0, inplace=True)
    df.bfill(axis=0, inplace=True)
    return df


def df_center2(df, xctrs, reference_trace):
    """Shift the x-axis of the data to align to max peak of reference
    Get index of reference column in df, which will be related to the index
    in the xctrs array by a factor of -1 (no x column in the xctrs array)
    then shift each y-data column by the appropriate factor
    """
    ref_col_idx = df.columns.get_loc(reference_trace) - 1

    for i in range(len(df.columns) - 1):
        shft = xctrs[i][0] - xctrs[ref_col_idx][0]  # shift data relative to ref sample
        df.iloc[:, (i + 1)] = df.iloc[:, (i + 1)].shift(-shft)

    # Fill in ends of data after dataframe shift
    df.ffill(axis=0, inplace=True)
    df.bfill(axis=0, inplace=True)
    return df


def df_center_reverse(df, xctrs, reference_trace):
    """Undo df_center2"""
    ref_col_idx = df.columns.get_loc(reference_trace) - 1

    for i in range(len(df.columns) - 1):
        shft = xctrs[i][0] - xctrs[ref_col_idx][0]  # shift data relative to ref sample
        df.iloc[:, (i + 1)] = df.iloc[:, (i + 1)].shift(shft)

    # Fill in ends of data after dataframe shift
    df.ffill(axis=0, inplace=True)
    df.bfill(axis=0, inplace=True)
    return df


def find_deriv(df, flip, window_length=5):
    """Adds the 2nd derivative of the chosen signal to the DataFrame
    Window_length=5 is recommended from our studies"""

    proteins = list(df.columns)[1:]
    # print("Flip inside find deriv: \n", flip)
    for i in proteins:
        if flip:
            # negative if want flipped
            dd = -1 * savgol_filter(
                df[i], deriv=2, window_length=window_length, polyorder=3
            )
        else:
            dd = savgol_filter(df[i], deriv=2, window_length=window_length, polyorder=3)

        df.loc[:, i] = dd

    return df


def smooth_and_deriv(df, order=0, window_length=5, flip=False):
    """Smooths and adds any derivative (0-4) of the chosen signal to the DataFrame"""

    proteins = list(df.columns)[1:]

    for i in proteins:
        if flip:
            # negative if want flipped
            dd = -1 * savgol_filter(
                df[i], deriv=order, window_length=window_length, polyorder=3
            )
        else:
            dd = savgol_filter(
                df[i], deriv=order, window_length=window_length, polyorder=3
            )

        df.loc[:, i] = dd

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
    return df


def combine_uploaded_dfs(prev_df, df, cap=False, new_x=False):
    """
    To enable files to be added after an initial upload, we
    need to assimilate x-axis from each source.  This is accomplished
    by creating a multiple x, y set for each dataframe, concatenating
    them together, and then running the many_x_y_to_x_many_y function
    to recombine to a common x-axis (with interpolation as necessary)
    """
    prev_df = x_many_y_to_many_x_y(prev_df)

    # concatenating dfs won't work if they have cols with same names
    df1, df2 = rename_dup_cols_in_two_dfs(prev_df, df)
    df = pd.concat([df1, df2], axis=1)

    df = many_x_y_to_x_many_y(df, cap=cap, new_x=new_x)
    df.reset_index(drop=True, inplace=True)
    return df
