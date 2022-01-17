import numpy as np
import pandas as pd


def df_area_norm(df):
    """Normalize to area of 1 to give intuitive feel for peak area fraction"""

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
