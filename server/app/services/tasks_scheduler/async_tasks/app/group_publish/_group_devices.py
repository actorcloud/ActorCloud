from typing import List, Any, Dict, AnyStr, Tuple

from actor_libs.tasks.task import get_task_result
from actor_libs.types import TaskResult
from actor_libs.http_tools import AsyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from ._sql_statements import (
    insert_group_control_log_sql, query_group_of_uid_sql, query_group_devices_sql,
    update_devices_control_log_sql, update_group_control_log_sql
)
from .. import postgres, project_config


__all__ = [
    'mqtt_group_publish_info', 'insert_group_control_log',
    'group_emqx_publish', 'update_group_control_log'
]


async def mqtt_group_publish_info(
        request_dict: Dict, group_control_log_id: int) -> Tuple[List, AnyStr]:
    group_uid = request_dict['groupID']
    base_payload = {
        'qos': 1,
        'topic': 'inbox',
        'task_id': request_dict['taskID'],
        'payload': request_dict['payload'],
        'protocol': request_dict['protocol'],
        'productID': request_dict['productID'],
        'tenantID': request_dict['tenantID'],
        'groupControlLogIntID': group_control_log_id,
        'userIntID': request_dict['userIntID'],
        'publishTime': request_dict['publishTime']
    }
    if request_dict['protocol'] == 'lwm2m':
        base_payload['callback'] = project_config['LWM2M_CALLBACK_URL']
    else:
        base_payload['callback'] = project_config['MQTT_CALLBACK_URL']

    group_devices_publish = []
    publish_append = group_devices_publish.append
    group_devices_info = await postgres.fetch(
        sql=query_group_devices_sql.format(group_uid=group_uid),
        fetch_type='many')
    base_task_id = base_payload['task_id'][:-4]
    for index, (device_id, device_uid) in enumerate(group_devices_info):
        publish_info = {
            **base_payload, 'deviceID': device_uid,
            'deviceIntID': device_id,
            'task_id': f"{base_task_id}{index:04}"
        }
        publish_append(publish_info)
    if group_devices_publish:
        insert_status = await _insert_group_devices_control_log(group_devices_publish)
        if not insert_status:
            group_devices_publish = []
    publish_url = project_config['MQTT_PUBLISH_URL']
    return group_devices_publish, publish_url


async def insert_group_control_log(request_dict) -> Any:
    group_uid = await postgres.fetch(
        query_group_of_uid_sql.format(group_uid=request_dict['groupID']),
        fetch_type='val')
    if group_uid:
        publish_log = {
            'createAt': request_dict['publishTime'],
            'topic': 'inbox',
            'taskID': request_dict['taskID'],
            'payload': request_dict['payload'],
            'publishStatus': 1,
            'groupID': group_uid,
            'userIntID': request_dict['userIntID']
        }
        group_control_id = await postgres.fetch_val(
            insert_group_control_log_sql.format(**publish_log))
    else:
        group_control_id = None
    return group_control_id


async def group_emqx_publish(group_devices_publish, publish_url) -> TaskResult:
    auth = project_config['EMQX_AUTH']
    async with AsyncHttp(auth=auth) as actor_http:
        publish_responses = await actor_http.post_url_args(
            url=publish_url, requests_json=group_devices_publish)
    task_result = await _handle_group_publish_response(publish_responses)
    return task_result


async def update_group_control_log(group_control_id: int) -> None:
    """ Update group publish with fail status """

    await postgres.execute(
        sql=update_group_control_log_sql.format(
            group_control_id=group_control_id))


async def _insert_group_devices_control_log(group_devices_publish) -> bool:
    device_control_columns = [
        'createAt', 'taskID', 'publishStatus', 'topic', 'payload', 'userIntID',
        'deviceIntID', 'groupControlLogIntID'
    ]
    group_devices_control = [
        (publish_info.pop('publishTime'),
         publish_info['task_id'], 1,
         publish_info['topic'], publish_info['payload'],
         publish_info.pop('userIntID'),
         publish_info.pop('deviceIntID'),
         publish_info.pop('groupControlLogIntID'))
        for publish_info in group_devices_publish
    ]
    execute_status = await postgres.copy_records_to_table(
        table_name='client_publish_logs',
        records=group_devices_control,
        columns=device_control_columns)
    return execute_status


async def _handle_group_publish_response(publish_responses: List) -> TaskResult:
    success, failed = 0, 0
    failed_devices = []
    failed_devices_append = failed_devices.append
    for response in publish_responses:
        handled_response = handle_emqx_publish_response(response)
        if handled_response.get('status') == 3:
            success += 1
        else:
            task_id = handled_response.get('taskID', '')
            failed_devices_append(task_id)
            failed += 1
    if failed_devices:
        await postgres.execute(
            sql=update_devices_control_log_sql.format(
                task_uids=','.join(set(failed_devices))))
    if success != 0:
        task_result = get_task_result(
            status=3,
            message='Group publish success',
            result={
                'success': success,
                'failed': failed
            })
    else:
        task_result = get_task_result(
            status=4,
            message='Group publish failed',
            result={
                'success': success,
                'failed': failed
            })
    return task_result
