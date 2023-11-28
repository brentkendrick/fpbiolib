import numpy as np
import pandas as pd
import math


# SHRINK DATASET FOR FASTER VISUALIZATION
# function to take a 1-D array and create x limits to 2nd decimal


def x_reduced(x_r):
    # We're going to interpolate the data to adjust all cgms to same x-interval, so will need to create a common spacing within the interpolated range
    import math

    desired_x_size = 5000  # number of desired datapoints per column (shorter gives faster processing at expense of resolution)
    cur_x_size = x_r.size  # current number of datapoints per column
    data_spacing = abs(x_r[-1] - x_r[0]) / desired_x_size

    new_x_start = (
        math.ceil(x_r[0] * 100) / 100
    )  # mult then div by 100 to get sig figs we want
    new_x_end = (
        math.floor(x_r[-1] * 100) / 100
    )  # mult then div by 100 to get sig figs we want
    return np.arange(
        new_x_start, new_x_end, data_spacing
    )  # new x-data spacing/range


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
