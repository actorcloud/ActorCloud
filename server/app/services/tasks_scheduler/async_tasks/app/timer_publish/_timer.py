from typing import List, Dict

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
    update_sql = f"""
        UPDATE "timer_publish"
        SET "taskStatus"=3
        WHERE timer_publish.id = ANY ('{set(crontab_ids)}'::int[])
    """
    await postgres.execute(update_sql)
