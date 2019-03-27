import arrow

from actor_libs.tasks.task import get_task_result
from actor_libs.types import TaskResult
from .sql_statement import (
    datapoint_event_hour_aggr_sql, datapoint_event_day_aggr_sql,
    datapoint_event_month_aggr_sql
)
from .. import postgres
from .. import project_config


__all__ = ['datapoint_event_aggr']


async def datapoint_event_aggr() -> TaskResult:
    aggr_result = {}
    date_now = arrow.now(tz=project_config['TIMEZONE'])
    aggr_result['datapoint_hour'] = await postgres.execute(
        datapoint_event_hour_aggr_sql
    )
    if date_now.hour == 0:
        aggr_result['datapoint_day'] = await postgres.execute(
            datapoint_event_day_aggr_sql
        )
    if date_now.day == 1 and date_now.hour == 0:
        aggr_result['datapoint_month'] = await postgres.execute(
            datapoint_event_month_aggr_sql
        )
    aggr_status = aggr_result.values()
    if aggr_status and all(aggr_status):
        task_result = get_task_result(
            status=3, message='Data point event aggr success', result=aggr_result
        )
    else:
        task_result = get_task_result(
            status=4, message='Data point event aggr failed', result=aggr_result
        )
    return task_result
