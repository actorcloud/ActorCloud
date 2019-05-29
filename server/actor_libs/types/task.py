from typing import (
    MutableMapping, Callable, Union, Awaitable, Dict, Any
)


__all__ = ['FaustApp', 'TaskRegistry', 'TaskResult']

TaskRegistry = MutableMapping[str, Callable[..., Awaitable]]
TaskResult = Union[Dict[str, Union[Union[int, str, dict], Any]], Dict[str, Union[dict, Any]]]
