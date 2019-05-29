from actor_libs.types import DictCodeCache
from ._dict_code import cache_dict_code


class Cache:
    _instance = None
    _dict_code_cache: DictCodeCache = {}
    models_schema_cache = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Cache, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def dict_code(self):
        if not self._dict_code_cache:
            self._dict_code_cache = cache_dict_code()
        return self._dict_code_cache
