import json

from app.core.cache import redis_client


class CacheService:

    @staticmethod
    def get(key: str):
        value = redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    @staticmethod
    def set(
        key: str,
        value,
        expire: int = 300,
    ):
        redis_client.set(
            key,
            json.dumps(value),
            ex=expire,
        )

    @staticmethod
    def delete(key: str):
        redis_client.delete(key)