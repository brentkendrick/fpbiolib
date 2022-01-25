import os

# Redis default
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


# Defaults for flask only server
ENV = os.getenv("FLASK_ENV", "development")
DEBUG = os.getenv("FLASK_DEBUG", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
