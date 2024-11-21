import os
import json
import hashlib
import warnings
import redis
import gzip
import pandas as pd
import plotly.utils
from diskcache import Cache
from contextlib import contextmanager
import pyarrow.feather as feather
import tempfile
import pickle
from io import BytesIO


cache = Cache(directory=None)  # Uses RAM only
# cache = Cache(directory='/tmp/cache') # Uses hybrid caching (RAM + disk)


# Context manager to initialize Redis
@contextmanager
def redis_connection():
    """
    Context manager that initializes and provides a Redis connection.
    If Redis is unavailable, it falls back to DiskCache which shows similar speed performace to Redis.
    """
    redis_instance = None
    try:
        # Attempt to connect to Redis
        redis_instance = redis.StrictRedis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
        redis_instance.ping()
        print("Redis is active!")
        yield redis_instance
    except Exception:
        # Fall back to DiskCache if Redis is unavailable
        warnings.warn("Using DiskCache")
        redis_instance = cache
        yield redis_instance
    finally:
        # Optionally, handle any cleanup or connection closing here if needed
        if redis_instance:
            print("Closing Redis connection (or DiskCache)...")
            # No explicit close needed for Redis or DiskCache in this case
            pass

class redis_store:
    """
    Save data to Redis or DiskCache (RAM) using specified method below.
    """

    @staticmethod
    def _hash(serialized_obj):
        """Compute a SHA-512 hash for the serialized object."""
        return hashlib.sha512(serialized_obj).hexdigest()

    @staticmethod
    def pickle_save(value, key="specify_key"):
        """
        Pickle and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. Fastest of the class options.
        """
        if isinstance(value, pd.DataFrame):
            value_type = "pd.DataFrame"
            serialized_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"
        with redis_connection() as r:
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", value_type)

    @staticmethod
    def pickle_load(key):
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                value = pickle.loads(serialized_value)  # type: ignore
            elif value_type == "json-serialized":
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value


    @staticmethod
    def pickle_serialize_save(value, key="specify_key"):
        """
        Pickle serialize and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. ~ 4% slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            # Serialize Pandas DataFrame to bytes using pickle
            with BytesIO() as buffer:
                pickle.dump(value, buffer)
                buffer.seek(0)
                serialized_value = buffer.read()  # Extract the serialized bytes
            value_type = "pd.DataFrame"
        else:
            # Serialize non-DataFrame value using Plotly JSON encoder
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"
        
        # Save both the serialized data and its type to Redis or DiskCache
        with redis_connection() as r:
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", value_type)

    @staticmethod
    def pickle_serialize_load(key):
        """
        Load and deserialize the value from Redis (or DiskCache) using the specified key.
        Handles both Pandas DataFrame and other JSON-serialized objects.
        """
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                # Deserialize the Pandas DataFrame using pickle
                with BytesIO(serialized_value) as buffer: # type: ignore
                    value = pickle.load(buffer)
            elif value_type == "json-serialized":
                # Deserialize the JSON data
                value = json.loads(serialized_value.decode("utf-8")) # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    @staticmethod
    def feather_save(value, key="specify_key"):
        """
        Feather serialize and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. ~ 1.7X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            # Serialize DataFrame as a Parquet file in memory
            with BytesIO() as buffer:
                feather.write_feather(value, buffer) # Write DataFrame to a buffer
                buffer.seek(0)
                serialized_value = buffer.read() # Extract the serialized bytes
                value_type = "pd.DataFrame"
        else:
            # Serialize other JSON-serializable objects
            serialized_value = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder).encode("utf-8")
            value_type = "json-serialized"

        # Use the context manager to interact with Redis (or FakeRedis)
        with redis_connection() as r:
            # Save the compressed value and its type
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", value_type)   

    @staticmethod
    def feather_load(key):
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                # Deserialize the Parquet DataFrame
                with BytesIO(serialized_value) as buffer: # type: ignore
                    value = feather.read_feather(buffer)  # type: ignore

            elif value_type == "json-serialized":
                # Decompress and deserialize JSON
                decompressed_json = brotli.decompress(serialized_value)
                value = json.loads(decompressed_json)
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    @staticmethod
    def pd_feather_save(value, key="specify_key"):
        """
        Pandas implementation of feather serialize and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. ~ 1.7X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            # Serialize DataFrame as a Parquet file in memory
            with BytesIO() as buffer:
                value.to_feather(buffer) # Feather doesn't support compression
                buffer.seek(0)
                serialized_value = buffer.read()
                value_type = "pd.DataFrame"
        else:
            # Serialize other JSON-serializable objects
            serialized_value = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder).encode("utf-8")
            value_type = "json-serialized"

        # Use the context manager to interact with Redis (or FakeRedis)
        with redis_connection() as r:
            # Save the compressed value and its type
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", value_type)   

    @staticmethod
    def pd_feather_load(key):
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                # Deserialize the Parquet DataFrame
                with BytesIO(serialized_value) as buffer: # type: ignore
                    value = pd.read_feather(buffer)  # type: ignore

            elif value_type == "json-serialized":
                # Decompress and deserialize JSON
                decompressed_json = brotli.decompress(serialized_value)
                value = json.loads(decompressed_json)
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    # Data compression methods (better for website based data transfers)
    @staticmethod
    def pickle_compress_save(value, key="specify_key"):
        """
        Pickle and compress (approximately 30% compression) and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. ~ 9X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            type = "pd.DataFrame"
            serialized_value = gzip.compress(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            type = "json-serialized"
        with redis_connection() as r:
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", type)

    @staticmethod
    def pickle_decompress_load(key):
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                value = pickle.loads(gzip.decompress(serialized_value))  # type: ignore
            elif value_type == "json-serialized":
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value 

    @staticmethod
    def parquet_gzip_save(value, key="specify_key"):
        """
        Parquet save a value to the storage backend with gzip compression. and compress (approximately 30% compression) and save the value to Redis (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects. ~ 10X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            # Serialize DataFrame as a Parquet file in memory
            buffer = BytesIO()
            value.to_parquet(buffer, compression="gzip")  # Use Brotli for Parquet compression
            buffer.seek(0)
            serialized_value = buffer.read()
            value_type = "pd.DataFrame"
        else:
            # Serialize other JSON-serializable objects
            serialized_value = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder).encode("utf-8")
            value_type = "json-serialized"

        # Use the context manager to interact with Redis (or FakeRedis)
        with redis_connection() as r:
            # Save the compressed value and its type
            r.set(f"_value_{key}", serialized_value)
            r.set(f"_type_{key}", value_type)   

    @staticmethod
    def parquet_gzip_load(key):
        """Load a value from the storage backend with parquet gzip decompression."""
        with redis_connection() as r:
            value_type = r.get(f"_type_{key}")
            serialized_value = r.get(f"_value_{key}")
        
        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")
        
        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode('utf-8')  # Convert byte string to regular string

            if value_type == "pd.DataFrame":
                # Deserialize the Parquet DataFrame
                value = pd.read_parquet(BytesIO(serialized_value))  # type: ignore
            elif value_type == "json-serialized":
                # Decompress and deserialize JSON
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value
    