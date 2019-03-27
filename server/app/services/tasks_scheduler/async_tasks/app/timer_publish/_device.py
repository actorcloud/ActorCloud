from collections import defaultdict
from typing import List, Dict

from ._sql_statements import query_ids_device_sql
from .. import postgres


__all__ = ['handle_device_timer_task', 'get_ids_device_info']


async def handle_device_timer_task(due_task: Dict, device_info: Dict):
    due_task.update(device_info)
    del due_task['groupID']


async def get_ids_device_info(query_device_ids: List[int]) -> Dict:
    """
    Query device info by device id
    Return a dict like this {"deviceIntID": {"deviceIntID": "deviceID":, "productID":,"protocol":}}
    """

    if not query_device_ids:
        return {}

    query_results = await postgres.fetch_many(
        sql=query_ids_device_sql.format(
            client_ids=','.join([str(i) for i in query_device_ids])
        )
    )
    if query_results:
        device_info = defaultdict(dict)
        for result in query_results:
            device_info[result['deviceIntID']] = dict(result)
    else:
        device_info = {}
    return device_info
