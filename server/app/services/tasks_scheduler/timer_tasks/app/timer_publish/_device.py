from collections import defaultdict
from typing import List, Dict

from actor_libs.database.async_db import db
from actor_libs.http_tools.async_http import AsyncHttp
from ..config import project_config


__all__ = ['get_devices_info', 'build_device_publish_info', 'devices_publish']


async def get_devices_info(devices_id: List[int]) -> Dict:
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
    query_results = await db.fetch_many(sql=device_query_sql)
    if query_results:
        device_info = defaultdict(dict)
        for result in query_results:
            device_info[result['deviceIntID']] = dict(result)
    else:
        device_info = {}
    return device_info


async def build_device_publish_info(time_task, device_info):
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


async def devices_publish(publish_info: List[Dict]) -> Dict:
    url = project_config['PUBLISH_TASK_URL']
    async with AsyncHttp() as async_http:
        await async_http.post_url_args(url=url, requests_json=publish_info)
    # todo task handle
    publish_result = {
        'success': len(publish_info),
        'failed': 0
    }
    return publish_result
