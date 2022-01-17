"""
If running local redis, install for WSL2 using instructions here: https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database

To start the local redis server: sudo service redis-server start
To stop: sudo service redis-server stop
"""
import pandas as pd
import json
from redis import Redis

# from config.settings import REDIS_URL

from decouple import config

REDIS_URL = config('REDIS_URL')

r = Redis.from_url(REDIS_URL, decode_responses=True)  # use if running docker

# r = Redis(host='127.0.0.1', port=6379, db=0) #use if running local redis


if r.ping():
    message = "Redis ok "

else:
    message = "Redis failed ..."

print(message)

# @cache.memoize()  #Use with flask_caching only, uncertain of benefit
def write_dataframe(df, df_name):
    """
    Write dataframe to redis cache.
    """
    # print('Calling write_dataframe')
    timeout = None  # None, or time in seconds until redis cache is destroyed
    r.set(
        df_name, df.to_json(), ex=timeout
    )  # r.set(key, value, ex time expiry values are in seconds)


# @cache.memoize()
def read_dataframe(df_name):
    """
    Read dataframe from redis cache
    """
    # print('Calling read_dataframe')
    df = r.get(df_name)
    df = pd.read_json(df)
    return df


def write_numeric(num, name):
    """
    Write dataframe to redis cache.
    """
    # json dumps needs to be int or str, not float, so...convert all to string to be flexible!
    num = str(num)

    timeout = None  # None, or time in seconds until redis cache is destroyed

    r.set(
        name, json.dumps(num), ex=timeout
    )  # r.set(key, value, ex time expiry values are in seconds)


# @cache.memoize()
def read_numeric(name):
    """
    Read dataframe from redis cache
    """
    # print('Calling read_dataframe')
    json_number = r.get(name)
    return float(json.loads(json_number))
