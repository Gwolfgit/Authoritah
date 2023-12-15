from typing import Union, Optional, Any, List
from uuid import uuid4
import time

import redis.StrictRedis


class LooseRedis:
    """
    A drop-in replacement for the redis dependency. Stores data in (less persistent) memory.
    The methods mimic common Redis operations.
    """

    def __init__(self,
                 namespace: str = 'main',
                 expire: Union[int, None] = None,
                 preserve_expiration: Optional[bool] = False,
                 **redis_kwargs: Any) -> None:
        self.namespace = namespace + "-" + uuid4().hex
        self.expire = expire
        self.memory = {}
        self.expiry = {}

    def set(self, formatted_key: str, store_value: Union[str, int, bytes], ex: int = None) -> None:
        """
        Sets a value in the in-memory dictionary with optional expiration.

        :param formatted_key: The key under which the value is stored.
        :param store_value: The value to be stored.
        :param ex: Expiration time in seconds.
        """
        namespaced_key = f"{self.namespace}:{formatted_key}"
        self.memory[namespaced_key] = store_value
        if ex:
            self.expiry[namespaced_key] = time.time() + ex

    def delete(self, formatted_key: str) -> None:
        """
        Deletes a key-value pair from the in-memory dictionary.

        :param formatted_key: The key to be deleted.
        """
        namespaced_key = f"{self.namespace}:{formatted_key}"
        self.memory.pop(namespaced_key, None)
        self.expiry.pop(namespaced_key, None)

    def mget(self, formatted_keys: List[str]) -> List[Optional[Union[str, int, bytes]]]:
        """
        Retrieves values for multiple keys.

        :param formatted_keys: A list of keys to retrieve.
        :return: A list of values corresponding to the provided keys.
        """
        return [self.memory.get(f"{self.namespace}:{key}") for key in formatted_keys]

    def scan_iter(self, match: str) -> List[str]:
        """
        Yields keys matching a pattern.

        :param match: The pattern to match keys against.
        :return: A list of keys matching the pattern.
        """
        return [key for key in self.memory if key.startswith(match)]

    def _cleanup_expired_keys(self) -> None:
        """
        Internal method to remove expired keys.
        """
        current_time = time.time()
        expired_keys = [key for key, expiry in self.expiry.items() if expiry < current_time]
        for key in expired_keys:
            self.delete(key.split(':', 1)[1])


redis.StrictRedis = LooseRedis
