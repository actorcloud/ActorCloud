import arrow

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import get_task_result
from actor_libs.types import TaskResult
from .sql_statements import (
    api_hour_count_sql, api_day_count_sql, api_month_count_sql
)
from ..config import project_config


__all__ = ['api_count_task']


async def api_count_task() -> TaskResult:
    aggr_result = {}
    date_now = arrow.now(tz=project_config['TIMEZONE'])

    aggr_result['api_count_hour'] = await _hour_api_count_aggr()
    if date_now.hour == 0:
        aggr_result['api_count_day'] = await _day_api_count()
    if date_now.day == 1 and date_now.hour == 0:
        aggr_result['api_count_month'] = _month_api_count()
    # aggr_result: {'api_count_hour': True}
    aggr_status = aggr_result.values()
    # status 3:success 4:failure
    if aggr_status and all(aggr_status):
        task_result = get_task_result(
            status=3, message='Api count aggr success', result=aggr_result)
    else:
        task_result = get_task_result(
            status=4, message='Api count aggr failed', result=aggr_result)
    return task_result


async def _hour_api_count() -> bool:
    execute_result = await db.execute(api_hour_count_sql)
    return execute_result


async def _day_api_count() -> bool:
    execute_result = await db.execute(api_day_count_sql)
    return execute_result


async def _month_api_count() -> bool:
    execute_status = await db.execute(api_month_count_sql)
    return execute_status
