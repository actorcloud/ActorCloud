from typing import (
    MutableMapping, Callable, Union, Awaitable, Dict, Any
)

from faust.types.app import AppT


__all__ = ['FaustApp', 'TaskRegistry', 'TaskResult']

FaustApp = AppT
TaskRegistry = MutableMapping[str, Callable[..., Awaitable]]
TaskResult = Union[Dict[str, Union[Union[int, str, dict], Any]], Dict[str, Union[dict, Any]]]
