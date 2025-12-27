from dogpile.cache import make_region

# Configure the cache region
# Here, we are using a simple in-memory cache, but you can configure other backends like Redis or Memcached.
# The expiration time is set to 1 hour (3600 seconds).
cache_region = make_region().configure(
    backend='dogpile.cache.memory',
    expiration_time=3600,
)
