from actor_libs.types.base import CacheDictCode
from ._dict_code import dict_code_cache


class Cache:
    _dictCodeCache: CacheDictCode = {}

    @property
    def dict_code(self):
        if not self._dictCodeCache:
            self._dictCodeCache = dict_code_cache()
        return self._dictCodeCache


cache = Cache()
