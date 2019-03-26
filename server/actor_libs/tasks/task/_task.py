from datetime import datetime
from typing import (
    Any, Awaitable, Callable, Mapping, Sequence, Dict, Tuple
)

from actor_libs.utils import generate_uuid
from ._processor import store_task
from ..model import TaskInfo
from actor_libs.types import FaustApp


__all__ = ['Task']


class Task:
    def __init__(self, func: Callable[..., Awaitable], app: FaustApp,
                 kwargs: Mapping) -> None:
        self.app = app
        self.func = func
        self.task_kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    async def delay(self, *args: Any, **kwargs: Any) -> Any:
        return await self.apply_async(args, kwargs)

    async def apply_async(self, args: Sequence, kwargs: Mapping) -> Dict:
        """ Register func and send to stream channel """

        task_info, task_is_store = await self._build_task_info(args, kwargs)
        # register func
        self.app.tasks_registry[task_info.taskName] = self.func
        if task_is_store:
            await store_task(postgres=self.app.db_engine, task_info=task_info)
        await self.app.tasks_channel.send(value=task_info)
        task_status = {'taskID': task_info.taskID}
        return task_status

    async def _build_task_info(self, args: Sequence,
                               kwargs: Mapping) -> Tuple[TaskInfo, bool]:

        task_name = self.task_kwargs.get('task_name', f'{self.func.__name__}')
        task_is_store = False if self.task_kwargs.get('task_ignore') else True
        task_id = kwargs.pop('task_id', None)
        if task_id:
            task_is_store = False
        else:
            task_id = generate_uuid()
        task_info = TaskInfo(
            taskID=task_id,
            createAt=datetime.now(),
            taskStatus=1,  # waiting
            taskName=task_name,
            arguments=args,
            keyword_arguments=kwargs)
        return task_info, task_is_store
