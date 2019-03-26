from actor_libs.types import CacheDictCode
from ._dict_code import dict_code_cache


class Cache:
    _instance = None
    _dict_code_cache: CacheDictCode = {}
    models_schema_cache = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Cache, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def dict_code(self):
        if not self._dict_code_cache:
            self._dict_code_cache = dict_code_cache()
        return self._dict_code_cache
