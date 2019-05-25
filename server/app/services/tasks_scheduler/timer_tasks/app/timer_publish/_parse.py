import json
from typing import List, Dict

from arrow import Arrow
from arrow import now as date_now, get as date_get
from arrow.parser import ParserError

from actor_libs.database.async_db import db
from ..config import project_config


__all__ = ['get_due_tasks']


async def get_due_tasks() -> List[int]:
    """ Get a list of tasks that should be run now """

    arrow_now = date_now(tz=project_config['TIMEZONE'])
    query_timer_publish_sql = """
    SELECT timer_publish.*
    FROM timer_publish
           JOIN users ON users.id = timer_publish."userIntID"
           JOIN tenants ON tenants."tenantID" = users."tenantID"
    WHERE "taskStatus" = 2
      AND users.enable = 1
      AND tenants.enable = 1
    """
    query_timer_tasks = await db.fetch_many(
        sql=query_timer_publish_sql
    )
    due_tasks_id: List[int] = []
    due_tasks_append = due_tasks_id.append
    if not query_timer_tasks:
        return due_tasks_id
    for timer_task in query_timer_tasks:
        is_due = await _tasks_is_due(arrow_now, timer_task)
        if is_due:
            due_tasks_append(timer_task.get('id'))
    return due_tasks_id


async def _tasks_is_due(arrow_now: Arrow, timer_task: Dict) -> bool:
    """
    Check if the task is due
    :return True if the task should be run now otherwise False
    """

    is_due = False
    interval_time = timer_task.get('intervalTime')
    crontab_time = timer_task.get('crontabTime')
    if timer_task.get('timerType') == 1 and crontab_time:
        # schedule time
        try:
            crontab_time = date_get(crontab_time)
            if all([crontab_time.year == arrow_now.year,
                    crontab_time.month == arrow_now.month,
                    crontab_time.day == arrow_now.day,
                    crontab_time.hour == arrow_now.hour,
                    crontab_time.minute == arrow_now.minute]):
                is_due = True
        except ParserError:
            is_due = False
    elif timer_task.get('timerType') == 2 and interval_time:
        interval_time = json.loads(interval_time)
        week_day = arrow_now.weekday()
        interval_minute = interval_time.get('minute')
        interval_hour = interval_time.get('hour')
        interval_weekday = interval_time.get('weekday')
        if all([interval_minute == arrow_now.minute,
                interval_hour is None, interval_weekday is None]):
            is_due = True
        elif all([interval_minute == arrow_now.minute,
                  interval_hour == arrow_now.hour,
                  interval_weekday is None]):
            is_due = True
        elif all([interval_minute == arrow_now.minute,
                  interval_hour == arrow_now.hour,
                  interval_weekday == week_day]):
            is_due = True

    return is_due
