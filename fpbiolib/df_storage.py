import hashlib
import io
import json
import os
import pickle
import warnings

import fakeredis

# import feather
import pandas as pd
import plotly
import redis

"""
Writing a custom function for feather
hass about 40% faster storage than using
pandas.DataFrame.to_feather..however
currently having dependency conflicts with feather
so abandoning for now in favor of the redis_store
approach outlined in the Dash docs:  https://dash.plotly.com/all-in-one-components
"""


# def df_to_feather(df, temp_fname):
#     """
#     Write dataframe to feather storage
#     """
#     return feather.write_dataframe(df, temp_fname)


# def df_fm_feather(temp_fname):
#     """
#     Read dataframe from feather storage
#     """
#     return feather.read_dataframe(temp_fname)


class redis_store:
    """Save data to Redis using the hashed contents as the key.
    Serialize Pandas DataFrames as memory-efficient Parquet files.

    Otherwise, attempt to serialize the data as JSON, which may have a
    lossy conversion back to its original type. For example, numpy arrays will
    be deserialized as regular Python lists.

    Connect to Redis with the environment variable `REDIS_URL` if available.
    Otherwise, use FakeRedis, which is only suitable for development and
    will not scale across multiple processes.
    """

    if "REDIS_URL" in os.environ:
        r = redis.StrictRedis.from_url(os.environ["REDIS_URL"])
        # print("REAL redis is running and the url is: ", os.environ["REDIS_URL"])
    else:
        warnings.warn("Using FakeRedis - Not suitable for Production Use.")
        r = fakeredis.FakeStrictRedis()

    @staticmethod
    def _hash(serialized_obj):
        return hashlib.sha512(serialized_obj).hexdigest()

    @staticmethod
    def save(value, key="specify_key"):
        if isinstance(value, pd.DataFrame):
            buffer = io.BytesIO()
            value.to_parquet(buffer, compression="gzip")
            buffer.seek(0)
            df_as_bytes = buffer.read()
            type = "pd.DataFrame"
            serialized_value = df_as_bytes
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            type = "json-serialized"

        redis_store.r.set(f"_value_{key}", serialized_value)
        redis_store.r.set(f"_type_{key}", type)

    @staticmethod
    def load(key):
        data_type = redis_store.r.get(f"_type_{key}")
        serialized_value = redis_store.r.get(f"_value_{key}")
        try:
            if data_type == b"pd.DataFrame":
                value = pd.read_parquet(io.BytesIO(serialized_value))
            else:
                value = json.loads(serialized_value)
        except Exception as e:
            print(e)
            print(f"ERROR LOADING {data_type - key}")
            raise e
        return value

    @staticmethod
    def pickle_save(value, key="specify_key"):
        if isinstance(value, pd.DataFrame):
            type = "pd.DataFrame"
            serialized_value = pickle.dumps(
                value, protocol=pickle.HIGHEST_PROTOCOL
            )
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            type = "json-serialized"

        redis_store.r.set(f"_value_{key}", serialized_value)
        redis_store.r.set(f"_type_{key}", type)

    @staticmethod
    def pickle_load(key):
        data_type = redis_store.r.get(f"_type_{key}")
        serialized_value = redis_store.r.get(f"_value_{key}")
        try:
            if data_type == b"pd.DataFrame":
                value = pickle.loads(serialized_value)
            else:
                value = json.loads(serialized_value)
        except Exception as e:
            print(e)
            print(f"ERROR LOADING {data_type - key}")
            raise e
        return value
