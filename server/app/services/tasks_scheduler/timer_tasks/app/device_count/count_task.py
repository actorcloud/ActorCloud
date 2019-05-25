import arrow

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import get_task_result
from actor_libs.types import TaskResult
from .sql_statements import devices_count_sql
from ..config import project_config


__all__ = ['device_count_task']


async def device_count_task() -> TaskResult:
    aggr_result = {}
    date_now = arrow.now(tz=project_config['TIMEZONE'])

    aggr_result['device_count_hour'] = await _hour_device_count()
    if date_now.hour == 0:
        aggr_result['device_count_day'] = await _day_device_count()
    if date_now.day == 1 and date_now.hour == 0:
        aggr_result['device_count_month'] = await _month_device_count()
    aggr_status = aggr_result.values()
    # status 3:success 4:failure
    if aggr_status and all(aggr_status):
        task_result = get_task_result(
            status=3, message='device count aggr success', result=aggr_result
        )
    else:
        task_result = get_task_result(
            status=4, message='device count aggr failed', result=aggr_result
        )
    return task_result


async def _hour_device_count() -> bool:
    hour_aggr_sql = devices_count_sql.format(
        table='device_count_hour', time_unit='hour'
    )
    execute_result = await db.execute(hour_aggr_sql)
    return execute_result


async def _day_device_count() -> bool:
    day_aggr_sql = devices_count_sql.format(
        table='device_count_day', time_unit='day'
    )
    execute_result = await db.execute(day_aggr_sql)
    return execute_result


async def _month_device_count() -> bool:
    month_aggr_sql = devices_count_sql.format(
        table='device_count_month', time_unit='month'
    )
    execute_status = await db.execute(month_aggr_sql)
    return execute_status
