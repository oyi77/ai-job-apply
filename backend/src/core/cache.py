from dogpile.cache import make_region
from ..config import config

# Configure the cache region
backend = config.cache_backend
backend_arguments = {}

if backend == "dogpile.cache.redis":
    # Parse redis_url to get host, port, db
    # redis://host:port/db
    try:
        from urllib.parse import urlparse
        url = urlparse(config.redis_url)
        backend_arguments = {
            "host": url.hostname or "localhost",
            "port": url.port or 6379,
            "db": int(url.path.lstrip("/")) if url.path else 0,
            "redis_expiration_time": config.cache_expiration_time,
            "distributed_lock": True,
        }
    except Exception as e:
        # Fallback to memory on config error
        print(f"Error configuring Redis cache: {e}. Falling back to memory.")
        backend = "dogpile.cache.memory"

cache_region = make_region().configure(
    backend=backend,
    expiration_time=config.cache_expiration_time,
    arguments=backend_arguments,
)
