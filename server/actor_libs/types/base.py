from asyncio import AbstractEventLoop
from typing import Any, Callable, Union, Dict

from yarl import URL


__all__ = ['EventLoop', 'JSONDecoder', 'JSONEncoder', 'StrOrURL', 'CacheDictCode']

EventLoop = AbstractEventLoop
JSONEncoder = Callable[[Any], str]
JSONDecoder = Callable[[str], Any]
StrOrURL = Union[str, URL]
CacheDictCode = Dict
