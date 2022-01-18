import base64
import io

from dash import html

import pandas as pd

from lib.dashapps.df_transforms import (
    df_reduced,
    many_x_y_to_x_many_y,
    x_many_y_interpolate,
    downcast_floats_and_ints,
)


from redis import Redis

from config.settings import REDIS_URL

r = Redis.from_url(REDIS_URL, decode_responses=True)

# r = redis.Redis(host='myapp-redis', port=6379, db=0) # use if running docker redis
# r = redis.Redis(host='127.0.0.1', port=6379, db=0) #use if running local redis
if r.ping():
    message = "Redis ok "

else:
    message = "Redis failed ..."

print(message)


# File parsing and temporary dataframe storage functions
def parse_data(contents, filename):
    """
    Parse uploaded tabular file and return dataframe.
    """

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+"
            )
    except Exception as e:
        print(e)
        raise

    # some dfs get read with a bunch of unnamed columns, preventing plotting and other dash viewing options!
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # drop rows that are all na values
    df.dropna(how="all", inplace=True)

    df.reset_index(drop=True, inplace=True)

    return downcast_floats_and_ints(df)


def parse_uploaded_traces(contents, filenames, changed_id):
    # Create empty list to enable multiple file concatination
    appended_df = []
    uploaded_trace_filenames = []
    for name in filenames:
        file_txt = name + "; "
        uploaded_trace_filenames.append(file_txt)
    uploaded_trace_filenames.insert(0, "Uploaded: ")

    if "x_many_y_button" in changed_id:
        # Let's run a time function to see where we can optimize
        from timeit import default_timer as time

        start = time()

        for content, filename in zip(contents, filenames):
            print("FILENAME: ", filename)
            df_i = parse_data(content, filename)
            # df_i = df_i.apply(pd.to_numeric, errors='coerce')
            # df_i.dropna(how = 'any', inplace = True)
            appended_df.append(df_i.iloc[:, 1:])
            x_data = df_i.iloc[:, 0]  # x-data for the merged dataset
        appended_df.insert(0, x_data)
        df_i_concat = pd.concat(appended_df, axis=1)
        df = df_i_concat.sort_values(by=df_i_concat.columns[0])
        df.reset_index(drop=True, inplace=True)

        df = x_many_y_interpolate(df)

        end = time()
        print("Time elapsed:", end - start)
        # df.to_csv('with_interpolation_downcast.csv')

    else:
        for content, filename in zip(contents, filenames):
            df_i = parse_data(content, filename)
            # df_i = df_i.apply(pd.to_numeric, errors='coerce')
            # some x,y pairs have differing lengths for x compared to y...this will fix the x,y pairs, getting rid of raggedy ends!
            # temp_df = pd.DataFrame()
            # n=0
            # for i in range(int(len(df_i.columns)/2)):
            #     temp_df = pd.concat([temp_df, (df_i.iloc[:, n:n+2].dropna())], axis=1)
            #     n+=2
            # df_i = temp_df
            df_i = many_x_y_to_x_many_y(df_i)
            df_i_y = df_i.iloc[:, 1:]
            x_data = df_i.iloc[:, 0]
            appended_df.append(df_i_y)
        appended_df.insert(0, x_data)

        df_i_concat = pd.concat(appended_df, axis=1)
        df = df_i_concat.sort_values(by=df_i_concat.columns[0])
        df.reset_index(drop=True, inplace=True)

    cols = pd.Series(df.columns)

    # rename any duplicate column names
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [
            dup + "." + str(i) if i != 0 else dup
            for i in range(sum(cols == dup))
        ]

    # rename the columns with the cols list.
    df.columns = cols.to_list()

    return uploaded_trace_filenames, df


# @cache.memoize()  #Use with flask_caching only, uncertain of benefit
def write_dataframe(df, df_name):
    """
    Write dataframe to redis cache.
    """
    print("Calling write_dataframe")
    timeout = None  # None, or time in seconds until redis cache is destroyed
    r.set(
        df_name, df.to_json(), ex=timeout
    )  # r.set(key, value, ex time expiry values are in seconds)


# @cache.memoize()
def read_dataframe(df_name):
    """
    Read dataframe from redis cache
    """
    print("Calling read_dataframe")
    df = r.get(df_name)
    df = pd.read_json(df)
    return df
