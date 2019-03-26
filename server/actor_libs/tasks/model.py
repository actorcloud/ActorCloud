from abc import ABC
from datetime import datetime
from typing import Sequence, Mapping, Callable, Awaitable, Any

from faust import Record

from actor_libs.types import TaskRegistry


class TaskInfo(Record, ABC):
    createAt: datetime
    taskID: str
    taskName: str
    taskStatus: int
    tasksRegistry: TaskRegistry = {}
    arguments: Sequence = []
    keyword_arguments: Mapping = {}

    async def __call__(self) -> Any:
        return await self.handler(*self.arguments, **self.keyword_arguments)

    @property
    def handler(self) -> Callable[..., Awaitable]:
        return self.tasksRegistry[self.taskName]
