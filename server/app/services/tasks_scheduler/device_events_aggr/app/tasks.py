from actor_libs.tasks.base import task
from actor_libs.types import TaskResult
from . import faust_app
from .lwm2m_protocol import item_event_aggr
from .other_protocol import datapoint_event_aggr


__all__ = ['device_events_aggr']


@task(app=faust_app, task_name='device_events_aggr')
async def device_events_aggr() -> TaskResult:
    task_result = await datapoint_event_aggr()
    task_result.update(await item_event_aggr())

    aggr_status = task_result.values()
    if aggr_status and all(aggr_status):
        task_result['taskStatus'] = 2
    else:
        task_result['taskStatus'] = 3
    return task_result
