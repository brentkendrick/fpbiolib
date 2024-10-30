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


# General cleanup for many csv files
def drop_df_col_row_na_unnamed(df):
    # drop rows, columns that are all na values
    df.dropna(how="all", axis=0, inplace=True)
    df.dropna(how="all", axis=1, inplace=True)
    # some dfs get read with a bunch of unnamed columns,
    # preventing plotting and other dash viewing options!
    if any(df.columns.str.contains("^Unnamed")):
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")].copy()

    df.reset_index(drop=True, inplace=True)
    return df


def sort_df_x_ascending(df):
    # ensure data is arranged so x-values are ascending
    if df.iloc[0, 0] > df.iloc[-1, 0]:  # type: ignore
        df.sort_values(by=df.columns[0], inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


# Reduce from float 64 to float 32 helps reduce file size
def fix_dups_conv_numeric_float32_df(df):
    # Downcasting will fail if dup headings
    df = fix_duplicate_col_names(df)

    # Ensure numeric columns to start
    df = df.apply(pd.to_numeric)

    fcols = df.select_dtypes("float").columns

    # can't have duplicate column headings or this will fail
    df[fcols] = df[fcols].apply(pd.to_numeric, downcast="float")

    return df


# Reduce from float 64 to float 32 helps reduce file size
def downcast_floats_and_ints(df):
    # Ensure numeric columns to start
    df = df.apply(pd.to_numeric)

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
                dup + "." + str(i) if i != 0 else dup for i in range(sum(cols == dup))
            ]

    # rename the columns with the cols list.
    df.columns = cols.to_list()
    return df


def rename_dup_cols_in_two_dfs_old(df1, df2):
    """Will rename df2 columns with _dup if the name
    is duplicated in df1 columns.  Assumes that
    both dataframes each have unique column names
    within themselves.
    """
    for i, val in enumerate(df2.columns):
        if val in df1.columns:
            df2.columns.values[i] = f"{val}_dup_name"
    return df2


def fix_dups(mylist, sep="", start=1, update_first=True):
    mylist_dups = {}
    # build dictionary containing val: [occurrences, suffix]
    for val in mylist:
        if val not in mylist_dups:
            mylist_dups[val] = [1, start - 1]
        else:
            mylist_dups[val][0] += 1

    # define function to update duplicate values with suffix, check if updated value already exists
    def update_val(val, num):
        temp_val = sep.join([str(x) for x in [val, num]])
        if temp_val not in mylist_dups:
            return temp_val, num
        else:
            num += 1
            return update_val(val, num)

    # update list
    for i, val in enumerate(mylist):
        if mylist_dups[val][0] > 1:
            mylist_dups[val][1] += 1
            if update_first or mylist_dups[val][1] > start:
                new_val, mylist_dups[val][1] = update_val(val, mylist_dups[val][1])
                mylist[i] = new_val

    return mylist


def rename_dup_cols_in_two_dfs(df1, df2):
    """Will rename df2 columns with _dup if the name
    is duplicated in df1 columns.  Assumes that
    both dataframes each have unique column names
    within themselves.
    """
    combined_cols = df1.columns.to_list() + df2.columns.to_list()
    # print("combined_cols: ", combined_cols)
    combined_cols_uniquified = fix_dups(
        combined_cols, sep=".", start=0, update_first=False
    )
    # print("combined_cols_uniqueified: ", combined_cols_uniquified)
    df1_len = len(df1.columns)
    for i, val in enumerate(df1.columns):
        df1.columns.values[i] = combined_cols_uniquified[i]
    for i, val in enumerate(df2.columns):
        df2.columns.values[i] = combined_cols_uniquified[i + df1_len]

    return df1, df2
