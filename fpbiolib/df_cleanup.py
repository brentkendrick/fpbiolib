import pandas as pd


# General cleanup for many csv files
def cleanup_df_import(df):
    # drop rows, columns that are all na values
    df.dropna(how="all", axis=0, inplace=True)
    df.dropna(how="all", axis=1, inplace=True)
    # some dfs get read with a bunch of unnamed columns,
    # preventing plotting and other dash viewing options!
    if any(df.columns.str.contains("^Unnamed")):
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")].copy()

    df.reset_index(drop=True, inplace=True)
    return df


# Reduce from float 64 to float 32 helps reduce file size
def downcast_floats_and_ints(df):
    fcols = df.select_dtypes("float").columns
    icols = df.select_dtypes("integer").columns

    # can't have duplicate column headings or this will fail
    df[fcols] = df[fcols].apply(pd.to_numeric, downcast="float")
    df[icols] = df[icols].apply(pd.to_numeric, downcast="integer")

    return df


def fix_duplicate_col_names(df, filename=None):
    cols = pd.Series(df.columns)

    # rename any duplicate column names

    if filename:
        for dup in cols[cols.duplicated()].unique():
            # print("duplicate: ", dup)
            cols[cols[cols == dup].index.values.tolist()] = [
                dup + "." + filename.split(".")[0] if i != 0 else dup
                for i in range(sum(cols == dup))
            ]

    else:
        for dup in cols[cols.duplicated()].unique():
            # print("duplicate: ", dup)
            cols[cols[cols == dup].index.values.tolist()] = [
                dup + "." + str(i) if i != 0 else dup
                for i in range(sum(cols == dup))
            ]

    # rename the columns with the cols list.
    df.columns = cols.to_list()
    return df


def rename_dup_cols_in_two_dfs(df1, df2):
    """Will rename df2 columns with _dup if the name
    is duplicated in df1 columns.  Assumes that
    both dataframes each have unique column names
    within themselves.
    """
    for i, val in enumerate(df2.columns):
        if val in df1.columns:
            df2.columns.values[i] = f"{val}_dup_name"
    return df2
