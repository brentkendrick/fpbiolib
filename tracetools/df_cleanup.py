import pandas as pd


# General cleanup for many csv files
def cleanup_df_import(df):
    # some dfs get read with a bunch of unnamed columns, preventing plotting and other dash viewing options!
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # drop rows that are all na values
    df.dropna(how="all", inplace=True)

    df.reset_index(drop=True, inplace=True)

    return df


# Reduce from float 64 to float 32 helps reduce file size
def downcast_floats_and_ints(df):

    fcols = df.select_dtypes("float").columns
    icols = df.select_dtypes("integer").columns

    df[fcols] = df[fcols].apply(pd.to_numeric, downcast="float")
    df[icols] = df[icols].apply(pd.to_numeric, downcast="integer")

    return df
