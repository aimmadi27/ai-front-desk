import json
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import settings

_pool: Optional[redis.ConnectionPool] = None


def get_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def get_client() -> redis.Redis:
    return redis.Redis(connection_pool=get_pool())


async def get(key: str) -> Optional[Any]:
    client = get_client()
    value = await client.get(key)
    return json.loads(value) if value else None


async def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = get_client()
    await client.setex(key, ttl_seconds, json.dumps(value))


async def delete(key: str) -> None:
    client = get_client()
    await client.delete(key)


async def close() -> None:
    if _pool:
        await _pool.disconnect()
