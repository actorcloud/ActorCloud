import asyncio

import uvloop

from actor_libs.tasks.base import APP
from actor_libs.tasks.model import TaskInfo
from actor_libs.database.async_db import AsyncPostgres
from .config import get_aggr_config


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

__all__ = ['project_config', 'postgres', 'faust_app', 'task_process']

project_config = get_aggr_config()
postgres = AsyncPostgres(
    host=project_config.get('POSTGRES_HOST'),
    port=project_config.get('POSTGRES_PORT'),
    user=project_config.get('POSTGRES_USER'),
    password=project_config.get('POSTGRES_PASSWORD'),
    database=project_config.get('POSTGRES_DATABASE'),
    min_size=2, max_size=5
)

faust_app = APP(
    id='device_events_aggr',
    loop=loop,
    enable_web=False,
    db_engine=postgres,
    broker=project_config['KAFKA_SERVERS'],
    autodiscover=['app.services.tasks_scheduler.device_events_aggr.app'],
    origin='app.services.tasks_scheduler.device_events_aggr.app'
)


async def task_process(stream_task: TaskInfo):
    stream_task.tasksRegistry = faust_app.tasks_registry
    return stream_task
