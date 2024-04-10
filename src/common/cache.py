from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 60 * 60
}

cache = Cache(config=config)
