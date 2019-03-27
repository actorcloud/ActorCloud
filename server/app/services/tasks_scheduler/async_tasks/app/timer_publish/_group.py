from collections import defaultdict
from typing import List, Dict

from ._sql_statements import query_uids_group_sql
from .. import postgres


__all__ = ['handle_group_timer_task', 'get_uids_group_info']


async def handle_group_timer_task(due_task: Dict, group_info: Dict):
    due_task.update(group_info)
    del due_task['deviceIntID']


async def get_uids_group_info(query_group_uids: List) -> Dict:
    """
    Query device info by group id
    return a dict like this {"groupIntID": {"groupIntID": ,"groupID":, "productID": ,"protocol":}}
    """

    if not query_group_uids:
        return {}
    query_results = await postgres.fetch_many(
        sql=query_uids_group_sql.format(group_uids=','.join(query_group_uids)))

    if query_results:
        group_info = defaultdict(dict)
        for result in query_results:
            group_info[result['groupID']] = dict(result)
    else:
        group_info = {}
    return group_info
