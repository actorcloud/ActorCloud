from typing import List, Dict

from ._sql_statements import update_crontab_task_sql
from .. import postgres


__all__ = ['get_timer_tasks', 'update_crontab_tasks']


async def get_timer_tasks(due_tasks_id: List[int]) -> List[Dict]:
    query_due_tasks_sql = f"""
    SELECT timer_publish.*, users."tenantID"
    FROM timer_publish
           JOIN users ON users.id = timer_publish."userIntID"
    WHERE timer_publish.id = ANY ('{set(due_tasks_id)}'::int[])
    """
    query_timer_tasks = await postgres.fetch_many(
        sql=query_due_tasks_sql
    )
    due_tasks = [dict(_task) for _task in query_timer_tasks]
    return due_tasks


async def update_crontab_tasks(crontab_ids: List):
    str_crontab_ids = ','.join(
        [str(i) for i in set(crontab_ids) if i]
    )
    await postgres.execute(
        update_crontab_task_sql.format(crontab_ids=str_crontab_ids)
    )
