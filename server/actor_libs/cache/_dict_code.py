from collections import defaultdict

from actor_libs.types import CacheDictCode
from app.models import DictCode


__all__ = ['dict_code_cache']


def dict_code_cache() -> CacheDictCode:
    record = defaultdict(dict)
    dict_code_values = DictCode.query \
        .with_entities(DictCode.code, DictCode.codeLabel,
                       DictCode.codeStringValue, DictCode.codeValue)\
        .all()

    for dict_code in dict_code_values:
        code, label, str_value, int_value = dict_code
        code_value = int_value if int_value is not None else str_value
        record[code][code_value] = label
    return record
