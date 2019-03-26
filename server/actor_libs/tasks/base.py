from typing import Any

import faust

from .model import TaskInfo
from .task import Task
from actor_libs.types import TaskRegistry, FaustApp


class APP(faust.App):
    def __init__(self, db_engine=None, **options: Any):
        self.db_engine = db_engine
        self.tasks_channel = self.channel(value_type=TaskInfo)
        self.tasks_registry: TaskRegistry = {}
        super().__init__(**options)


def task(app: FaustApp, **kwargs) -> Task:
    def decorate(func):
        task_registered = Task(func, app, kwargs)
        return task_registered

    return decorate
