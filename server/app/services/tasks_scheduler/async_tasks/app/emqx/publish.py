import json

from actor_libs.database.async_db import db
from actor_libs.emqx.publish.protocol import PROTOCOL_PUBLISH_JSON_FUNC
from actor_libs.http_tools import AsyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.tasks.backend import get_task_result
from actor_libs.types import TaskResult
from actor_libs.utils import generate_uuid
from .sql_statements import insert_publish_logs_sql
from ..config import project_config


# from ._sql_statements import insert_publish_logs_sql, update_publish_logs_sql


__all__ = ['device_publish_task']


async def device_publish_task(request_dict) -> TaskResult:
    """
    :param request_dict:
           required key: topic, prefixTopic,
                         payload, deviceID, tenantID, protocol
           optional key: streamID
    """
    request_dict['taskID'] = generate_uuid()  # emqx publish taskID
    device_uid = request_dict['deviceID']
    task_id = request_dict['taskID']
    if not request_dict.get('streamID'):
        request_dict['streamID'] = None
    # insert publish logs
    insert_sql = insert_publish_logs_sql.format(**request_dict)
    insert_status = await db.execute(sql=insert_sql)
    if not insert_status:
        message = f"insert {device_uid} publish logs errors!"
        return get_task_result(status=4, message=message)
    # get publish json
    request_dict['payload'] = json.loads(request_dict['payload'])
    publish_json_func = PROTOCOL_PUBLISH_JSON_FUNC.get(request_dict['protocol'])
    if not publish_json_func:
        message = f"{device_uid} publish not support this protocol"
        return get_task_result(status=4, message=message)
    publish_json = publish_json_func(request_dict)
    # emqx publish
    task_result = await _emqx_device_publish(publish_json, device_uid, task_id)
    return task_result


async def _emqx_device_publish(publish_json, device_uid, task_id):
    emqx_pub_url = project_config['EMQX_PUBLISH_URL']
    async with AsyncHttp(auth=project_config['EMQX_AUTH']) as async_http:
        response = await async_http.post(emqx_pub_url, json=publish_json)
    handled_response = handle_emqx_publish_response(response)
    base_result = {
        'deviceID': device_uid,
        'taskID': task_id
    }
    if handled_response['status'] == 3:
        task_result = get_task_result(
            status=3, message='Device publish success', result=base_result
        )
    else:
        error_message = handled_response.get('error') or 'Device publish failed'
        task_result = get_task_result(
            status=4, message=error_message, result=base_result
        )
        update_sql = update_publish_logs_sql.format(taskID=task_id, publishStatus=0)
        db.execute(sql=update_sql)
    return task_result
