from redis import ConnectionPool, Redis

from src.settings.redis import redis_settings


def get_client() -> Redis:
    pool = ConnectionPool(
        host=redis_settings.host,
        port=redis_settings.port,
        db=redis_settings.database,
        password=redis_settings.password,
    )
    return Redis(connection_pool=pool)


def set_cache(key: str, value: str, expires: int = 60) -> None:
    get_client().setex(key, expires, value)


def get_cache(key: str) -> str | None:
    return get_client().get(key)  # type: ignore[return-value]
