from typing import Dict, AnyStr, Tuple

import ujson

from actor_libs.emqx.publish.lwm2m_publish import (
    handle_control_payload, check_control_type
)
from actor_libs.http_tools import AsyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from ._sql_statements import (
    query_id_device_sql, insert_device_control_logs_sql, query_path_lwm2m_sql,
    update_device_control_logs_sql)
from .. import postgres, project_config


__all__ = [
    'mqtt_device_publish_info', 'lwm2m_device_publish_info',
    'handle_lwm2m_payload', 'insert_device_control_log',
    'single_device_publish', 'update_control_logs'
]


async def mqtt_device_publish_info(request_dict: Dict) -> Tuple[Dict, AnyStr]:
    callback = project_config['MQTT_CALLBACK_URL']
    publish_payload = {
        'qos': 1,
        'topic': request_dict['topic'],
        'callback': callback,
        'task_id': request_dict['taskID'],
        'payload': request_dict['payload'],
        'deviceID': request_dict['deviceID'],
        'protocol': request_dict['protocol'],
        'productID': request_dict['productID'],
        'tenantID': request_dict['tenantID'],
    }
    publish_url = project_config['MQTT_PUBLISH_URL']
    return publish_payload, publish_url


async def lwm2m_device_publish_info(
        request_dict: Dict, encrypt_payload: Dict) -> Tuple[Dict, AnyStr]:
    callback = project_config['LWM2M_CALLBACK_URL']
    encrypt_payload['taskID'] = request_dict['taskID']
    publish_url = project_config['LWM2M_PUBLISH_URL']

    publish_payload = {
        'payload': encrypt_payload,
        'callback': callback,
        'deviceID': request_dict['deviceID'],
        'productID': request_dict['productID'],
        'tenantID': request_dict['tenantID'],
    }
    return publish_payload, publish_url


async def handle_lwm2m_payload(request_dict) -> Tuple[Dict, Dict]:
    """
    Handle lwm2m publish payload,
    return publish payload(encrypted) and store payload(origin)
    """

    path = request_dict['path']
    control_type = request_dict['controlType']
    origin_payload, encrypt_payload = {}, {}
    payload = request_dict['payload']

    if path == '/19/1/0':
        temp_payload = ujson.loads(payload)
        temp_payload['task_id'] = request_dict['taskID']
        origin_payload = {
            'msgType': 'write',
            'path': path,
            'value': temp_payload,
            'valueType': 'Opaque'
        }
        # emqx require value dumps
        encrypt_payload = {
            **origin_payload, 'value': ujson.dumps(temp_payload)
        }
    else:
        lwm2m_item = await postgres.fetch_row(
            query_path_lwm2m_sql.format(
                path=path,
                tenantID=request_dict['tenantID'],
                deviceIntID=request_dict['deviceIntID']))
        if not lwm2m_item:
            return origin_payload, encrypt_payload

        item_operations = lwm2m_item['itemOperations']
        item_type = lwm2m_item['itemType']
        if check_control_type(control_type, item_operations):
            origin_payload, encrypt_payload = handle_control_payload(
                control_type=request_dict['controlType'],
                path=path,
                payload=payload,
                item_type=item_type,
            )
    return origin_payload, encrypt_payload


async def insert_device_control_log(request_dict, origin_payload=None) -> bool:
    """
    Insert mqtt and lwm2m device control log
    :param request_dict:
    :param origin_payload: payload before encrypted, only for lwm2m
    """

    device_id = await postgres.fetch_val(
        query_id_device_sql.format(deviceIntID=request_dict['deviceIntID']))
    if origin_payload:
        request_dict['payload'] = ujson.dumps(origin_payload)
    if device_id:
        control_log = {
            'createAt': request_dict['publishTime'],
            'taskID': request_dict['taskID'],
            'publishStatus': 1,
            'payload': request_dict['payload'],
            'userIntID': request_dict['userIntID'],
            'deviceIntID': device_id
        }
        protocol = request_dict['protocol']
        if protocol == 'lwm2m':
            control_log['topic'] = 'NULL'
            control_log['path'] = request_dict['path']
            control_log['controlType'] = request_dict['controlType']
        else:
            control_log['path'] = 'NULL'
            control_log['controlType'] = 1
            control_log['topic'] = request_dict.get('topic', 'inbox')
        execute_status = await postgres.execute(
            sql=insert_device_control_logs_sql.format(**control_log))
    else:
        execute_status = False
    return execute_status


async def single_device_publish(publish_payload, publish_url) -> Dict:
    auth = project_config['EMQ_AUTH']
    async with AsyncHttp(auth=auth) as actor_http:
        response = await actor_http.post_url(
            url=publish_url, json=publish_payload)
    publish_result = handle_emqx_publish_response(response)
    return publish_result


async def update_control_logs(task_id: AnyStr, status: int):
    update_sql = update_device_control_logs_sql.format(
        taskID=task_id, taskStatus=status)
    await postgres.execute(update_sql)
