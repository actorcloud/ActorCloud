from collections import defaultdict
from typing import List, Dict

from ._timer import get_timer_tasks
from .. import postgres


__all__ = ['timer_publish']


async def timer_publish(due_tasks_id: List[int]):
    publish_info = []
    due_tasks: List[Dict] = await get_timer_tasks(due_tasks_id)
    device_ids = []
    for time_task in due_tasks:
        device_ids.append(time_task.get('deviceIntID'))
    devices_info = await _get_devices_info(device_ids)
    for time_task in enumerate(due_tasks):
        device_info = devices_info[time_task.get('deviceIntID')]
        _info = await _build_publish_info(time_task, device_info)
        publish_info.append(_info)
    return due_tasks


async def _get_devices_info(devices_id: List[int]) -> Dict:
    """ Query devices info by devices id """

    if not devices_id:
        return {}
    device_query_sql = f"""
    SELECT 
       devices.id AS "deviceIntID", 
       lower(dict_code."enLabel") AS protocol, devices."tenantID"
       devices."productID", devices."deviceID"
    FROM devices
       JOIN products ON products."productID" = devices."productID"
       JOIN dict_code ON dict_code."codeValue" = products."cloudProtocol"
    WHERE dict_code.code = 'cloudProtocol'
      AND devices.blocked = 0
      AND devices.id = ANY ('{set(devices_id)}'::int[])
    """
    query_results = await postgres.fetch_many(sql=device_query_sql)
    if query_results:
        device_info = defaultdict(dict)
        for result in query_results:
            device_info[result['deviceIntID']] = dict(result)
    else:
        device_info = {}
    return device_info


async def _build_publish_info(time_task, device_info):
    prefix_topic = (
        f"/{device_info['protocol']}/{device_info['tenantID']}"
        f"/{device_info['productID']}/{device_info['deviceID']}/"
    )
    publish_dict = {
        'deviceID': device_info['deviceID'],
        'topic': time_task['topic'],
        'payload': time_task['payload'],
        'prefixTopic': prefix_topic,
        'protocol': device_info['protocol'],
        'tenantID': device_info['tenantID'],
        'timerTaskID': time_task['id'],
        'timerType': time_task['timerType']  # update crontab task status
    }
    return publish_dict
