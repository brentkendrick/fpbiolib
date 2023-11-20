import feather
import pandas as pd

"""
Writing a custom function for feather
hass about 40% faster storage than using
pandas.DataFrame.to_feather
"""


def df_to_feather(df, temp_fname):
    """
    Write dataframe to feather storage
    """
    return feather.write_dataframe(df, temp_fname)


def df_fm_feather(temp_fname):
    """
    Read dataframe from feather storage
    """
    return feather.read_dataframe(temp_fname)
