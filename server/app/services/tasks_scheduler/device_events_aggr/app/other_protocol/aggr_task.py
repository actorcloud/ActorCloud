import arrow

from actor_libs.tasks.task import get_task_result
from actor_libs.types import TaskResult
from .sql_statement import (
    device_events_hour_aggr_sql, device_events_day_aggr_sql,
    device_events_month_aggr_sql
)
from .. import postgres
from .. import project_config


__all__ = ['device_events_aggr']


async def device_events_aggr() -> TaskResult:
    aggr_result = {}
    aggr_result['device_events_hour'] = await postgres.execute(
        device_events_hour_aggr_sql
    )

    date_now = arrow.now(tz=project_config['TIMEZONE'])
    if date_now.hour == 0:
        aggr_result['device_events_day'] = await postgres.execute(
            device_events_day_aggr_sql
        )
    if date_now.day == 1 and date_now.hour == 0:
        aggr_result['device_events_month'] = await postgres.execute(
            device_events_month_aggr_sql
        )
    aggr_status = aggr_result.values()
    if aggr_status and all(aggr_status):
        task_result = get_task_result(
            status=3, message='Device events aggr success', result=aggr_result
        )
    else:
        task_result = get_task_result(
            status=4, message='Device events aggr failed', result=aggr_result
        )
    return task_result
