import json
import hashlib
import gzip
import pandas as pd
import plotly.utils
import pyarrow.feather as feather
import pickle
import time  # Needed for retry delays
from io import BytesIO


class DataCache:
    """
    Save data to a cache backend (e.g., Redis, DiskCache) 
    using the specified methods below.
    You can pass any cache-like object 
    (e.g., Redis, DiskCache, or even an in-memory dictionary) 
    when creating the DataCache instance.
    """

    def __init__(self, cache):
        """
        Initialize the DataCache with a cache backend.
        The cache backend must implement `set` and `get` methods.
        """
        self.cache = cache

    @staticmethod
    def _hash(serialized_obj):
        """Compute a SHA-512 hash for the serialized object."""
        return hashlib.sha512(serialized_obj).hexdigest()

    def atomic_pickle_save(self, value, key="specify_key"):
        """
        Atomically save the value by combining the serialized data and its type
        into a single payload.
        """
        if isinstance(value, pd.DataFrame):
            value_type = "pd.DataFrame"
            serialized_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"

        # Combine both into one payload
        payload = {
            "value": serialized_value,
            "type": value_type
        }
        # Serialize the payload in one operation
        combined_payload = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
        # Use a single key for the combined payload
        self.cache.set(f"_payload_{key}", combined_payload)

    def atomic_pickle_load(self, key):
        """
        Atomically load and deserialize the payload.
        """
        combined_payload = self.cache.get(f"_payload_{key}")
        if not combined_payload:
            raise ValueError(f"Key {key} not found in the cache.")

        # Deserialize the payload
        payload = pickle.loads(combined_payload)
        value_type = payload.get("type")
        serialized_value = payload.get("value")

        if value_type == "pd.DataFrame":
            return pickle.loads(serialized_value)
        elif value_type == "json-serialized":
            return json.loads(serialized_value)
        else:
            raise ValueError(f"Unknown type for key {key}: {value_type}")


    def pickle_save(self, value, key="specify_key"):
        """
        Pickle and save the value to the cache backend with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        """
        if isinstance(value, pd.DataFrame):
            value_type = "pd.DataFrame"
            serialized_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"

        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", value_type)

    def pickle_load(self, key):
        """
        Load and deserialize the value from the cache backend using the specified key.
        """
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in the cache.")

        try:
            # Decode the type if stored as bytes
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

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

    def pickle_serialize_save(self, value, key="specify_key"):
        """
        Pickle serialize and save the value to Redis (or DiskCache if Redis is unavailable)
        with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        ~ 4% slower than pickle_save.
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
        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", value_type)

    def pickle_serialize_load(self, key):
        """
        Load and deserialize the value from Redis (or DiskCache) using the specified key.
        Handles both Pandas DataFrame and other JSON-serialized objects.
        """
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        # Check for None or missing data, and raise an exception if not found
        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")

        try:
            # Handle comparison for both byte and string types (Redis vs DiskCache)
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

            if value_type == "pd.DataFrame":
                # Deserialize the Pandas DataFrame using pickle
                with BytesIO(serialized_value) as buffer:  # type: ignore
                    value = pickle.load(buffer)
            elif value_type == "json-serialized":
                # Deserialize the JSON data
                value = json.loads(serialized_value.decode("utf-8"))  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    def feather_save(self, value, key="specify_key"):
        """
        Feather serialize and save the value to Redis (or DiskCache if Redis is unavailable)
        with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        ~ 1.7X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            # Serialize DataFrame as a Parquet file in memory
            with BytesIO() as buffer:
                feather.write_feather(value, buffer)
                buffer.seek(0)
                serialized_value = buffer.read()
                value_type = "pd.DataFrame"
        else:
            # Serialize other JSON-serializable objects
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"

        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", value_type)

    def feather_load(self, key):
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")

        try:
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

            if value_type == "pd.DataFrame":
                with BytesIO(serialized_value) as buffer:  # type: ignore
                    value = feather.read_feather(buffer)  # type: ignore
            elif value_type == "json-serialized":
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    def pd_feather_save(self, value, key="specify_key"):
        """
        Pandas implementation of feather serialize and save the value to Redis (or DiskCache if Redis is unavailable)
        with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        ~ 1.7X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            with BytesIO() as buffer:
                value.to_feather(buffer)
                buffer.seek(0)
                serialized_value = buffer.read()
                value_type = "pd.DataFrame"
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"

        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", value_type)

    def pd_feather_load(self, key):
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")

        try:
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

            if value_type == "pd.DataFrame":
                with BytesIO(serialized_value) as buffer:  # type: ignore
                    value = pd.read_feather(buffer)  # type: ignore
            elif value_type == "json-serialized":
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    def pickle_compress_save(self, value, key="specify_key"):
        """
        Pickle and compress (approximately 30% compression) and save the value to Redis
        (or DiskCache if Redis is unavailable) with the specified key.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        ~ 9X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            type_str = "pd.DataFrame"
            serialized_value = gzip.compress(
                pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            )
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            type_str = "json-serialized"

        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", type_str)

    def pickle_decompress_load(self, key):
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")

        try:
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

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

    def parquet_gzip_save(self, value, key="specify_key"):
        """
        Parquet save a value to the storage backend with gzip compression.
        Handles both Pandas DataFrame and other JSON-serializable objects.
        ~ 10X slower than pickle_save.
        """
        if isinstance(value, pd.DataFrame):
            buffer = BytesIO()
            value.to_parquet(buffer, compression="gzip")
            buffer.seek(0)
            serialized_value = buffer.read()
            value_type = "pd.DataFrame"
        else:
            serialized_value = json.dumps(
                value, cls=plotly.utils.PlotlyJSONEncoder
            ).encode("utf-8")
            value_type = "json-serialized"

        self.cache.set(f"_value_{key}", serialized_value)
        self.cache.set(f"_type_{key}", value_type)

    def parquet_gzip_load(self, key):
        """Load a value from the storage backend with parquet gzip decompression."""
        value_type = self.cache.get(f"_type_{key}")
        serialized_value = self.cache.get(f"_value_{key}")

        if not value_type or not serialized_value:
            raise ValueError(f"Key {key} not found in Redis or DiskCache.")

        try:
            if isinstance(value_type, bytes):
                value_type = value_type.decode("utf-8")

            if value_type == "pd.DataFrame":
                value = pd.read_parquet(BytesIO(serialized_value))  # type: ignore
            elif value_type == "json-serialized":
                value = json.loads(serialized_value)  # type: ignore
            else:
                raise ValueError(f"Unknown type for key {key}: {value_type}")
        except Exception as e:
            print(f"Error loading key {key}: {e}")
            raise e

        return value

    def safe_pickle_save(self, value, key="specify_key", max_attempts=100, sleep_interval=0.1):
        """
        Save a value using pickle (or JSON serialization) and verify the save by reloading until
        the reloaded value matches the original.
        
        This method leverages the existing pickle_save and pickle_load methods and supports both
        Pandas DataFrames and JSON-serializable objects.

        Parameters:
            value: The object to be saved.
            key (str): The key under which the object is saved.
            max_attempts (int): Maximum number of verification attempts.
            sleep_interval (float): Seconds to wait between attempts.

        Returns:
            The reloaded value if the verification succeeds.

        Raises:
            RuntimeError: If after max_attempts the reloaded value does not match the original.
        """
        # Save the value using the standard pickle_save method
        # print("key inside cache_utils: ", key)
        self.atomic_pickle_save(value, key=key)

        for attempt in range(max_attempts):
            loaded_value = self.atomic_pickle_load(key)

            # For DataFrames, use .equals() for an exact comparison.
            if isinstance(value, pd.DataFrame):
                if loaded_value is not None and loaded_value.equals(value):
                    # print(f"pickled df is equivalent")
                    return loaded_value
            # For other JSON-serializable objects, use the normal equality operator.
            else:
                if loaded_value == value:
                    return loaded_value


            time.sleep(sleep_interval)
            print("dataframe not synced, resyncing...")
        raise RuntimeError(f"Value mismatch after {max_attempts} attempts.")
