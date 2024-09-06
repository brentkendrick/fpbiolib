import os

# Redis default
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
