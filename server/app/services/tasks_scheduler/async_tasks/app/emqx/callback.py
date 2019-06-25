import json
import logging
from datetime import datetime

from actor_libs.database.async_db import db
from actor_libs.http_tools.async_http import AsyncHttp
from .sql_statements import (
    query_base_devices_sql, insert_connect_logs_sql,
    update_publish_logs_sql, update_device_status_sql
)
from ..config import project_config
from ..extra import HttpException


__all__ = ['backend_callback']


logger = logging.getLogger(__name__)


async def backend_callback(request_dict):
    request_dict['callback_date'] = datetime.now()
    callback_action = request_dict.get('action')
    handle_action_funcs = {
        'client_connected': client_connected_callback,
        'client_disconnected': client_disconnected_callback,
        'message_acked': message_acked_callback,
    }
    if not handle_action_funcs.get(callback_action):
        raise HttpException(code=404)
    handle_action = handle_action_funcs[callback_action]
    await handle_action(request_dict)
    return {'status': 200}, 200


async def client_disconnected_callback(request_dict) -> None:
    device_info = await _query_device_info(
        request_dict.get('client_id'),
        request_dict.get('username'),
    )
    connect_dict = {
        'msgTime': request_dict['callback_date'],
        'deviceID': device_info['deviceID'],
        'tenantID': device_info['tenantID'],
        'connectStatus': 0,
        'IP': 'NULL'
    }
    update_device = {
        'deviceStatus': 0,
        'id': device_info['id']
    }
    await db.execute(insert_connect_logs_sql.format(**connect_dict))
    await db.execute(update_device_status_sql.format(**update_device))


async def client_connected_callback(request_dict) -> None:
    """ Device connected subscribe inbox topic """

    device_info = await _query_device_info(
        request_dict.get('client_id'),
        request_dict.get('username'),
    )
    if device_info['protocol'] == 'lwm2m':
        # if device protocol is lwm2m pass
        return

    auto_sub_topic = (
        f"/{device_info['protocol']}/{device_info['tenantID']}"
        f"/{device_info['productID']}/{device_info['deviceID']}/inbox"
    )
    request_json = {
        'topic': auto_sub_topic,
        'qos': 1,
        'client_id': device_info['deviceID']
    }
    emqx_sub_url = f"{project_config['EMQX_API']}/mqtt/subscribe"
    async with AsyncHttp(auth=project_config['EMQX_AUTH']) as async_http:
        response = await async_http.post_url(
            url=emqx_sub_url, json=request_json
        )
        logger.info(response)


async def message_acked_callback(request_dict) -> None:
    """ Update the publish status when the device receives the publish message """

    device_id = request_dict.get('client_id')
    payload = request_dict.get('payload')
    if not device_id or not payload:
        raise HttpException(code=404)
    try:
        load_payload = json.loads(payload)
    except Exception:
        raise HttpException(code=404)
    task_id = load_payload.get('task_id')
    if not task_id:
        raise HttpException(code=404)

    await db.execute(
        update_publish_logs_sql.format(publishStatus=2, taskID=task_id)
    )


async def _query_device_info(device_id, device_username):
    if not device_id or not device_username:
        raise HttpException(code=404, field='devices')
    filter_username_sql = """ AND devices."deviceUsername" = '{deviceUsername}' """
    device_query_sql = query_base_devices_sql + filter_username_sql
    query_result = await db.fetch_row(
        device_query_sql.format(deviceID=device_id, deviceUsername=device_username)
    )
    if not query_result:
        raise HttpException(404, field='device')
    device_info = dict(query_result)
    return device_info
