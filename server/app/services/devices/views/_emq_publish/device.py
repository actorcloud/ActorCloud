from typing import AnyStr, Dict

import ujson
from flask import current_app

from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.database.orm import db
from actor_libs.emqx.publish.lwm2m_publish import (
    get_lwm2m_item_by_path, handle_control_payload
)
from actor_libs.errors import FormInvalid
from actor_libs.tasks.task import get_task_result
from app.models import DeviceControlLog


__all__ = ['mqtt_device_publish', 'lwm2m_device_publish', 'lora_device_publish']


def mqtt_device_publish(request_dict) -> Dict:
    json_payload = request_dict['payload']
    request_dict['payload'] = ujson.loads(json_payload)
    device_control_log = DeviceControlLog()
    control_log = device_control_log.create(request_dict=request_dict)

    callback = current_app.config['MQTT_CALLBACK_URL']
    request_url = current_app.config['MQTT_PUBLISH_URL']
    request_payload = {
        'qos': 1,
        'topic': request_dict['topic'],
        'callback': callback,
        'task_id': request_dict['taskID'],
        'payload': json_payload,
        'deviceID': request_dict['deviceID'],
        'protocol': request_dict['protocol'],
        'productID': request_dict['productID'],
        'tenantID': request_dict['tenantID']
    }
    record = _emqx_device_publish(request_url, request_payload, control_log)
    return record


def lwm2m_device_publish(request_dict) -> Dict:
    control_type = request_dict['controlType']
    if control_type not in [2, 3, 4]:
        raise FormInvalid(field='controlType')
    payload: AnyStr = request_dict['payload']
    path = request_dict['path']

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
        encrypt_payload = {**origin_payload, 'value': ujson.dumps(temp_payload)}
    else:
        item_dict = get_lwm2m_item_by_path(
            path, request_dict['deviceIntID'],
            request_dict['tenantID'],
        )
        origin_payload, encrypt_payload = handle_control_payload(
            control_type, path, payload, item_dict['item_type']
        )
    request_dict['payload'] = origin_payload
    control_log = DeviceControlLog().create(request_dict)

    request_url = current_app.config['LWM2M_PUBLISH_URL']
    encrypt_payload['taskID'] = request_dict['taskID']
    request_payload = {
        'payload': encrypt_payload,
        'callback': current_app.config['LWM2M_CALLBACK_URL'],
        'deviceID': request_dict['deviceID'],
        'productID': request_dict['productID'],
        'tenantID': request_dict['tenantID']
    }
    record = _emqx_device_publish(request_url, request_payload, control_log)
    return record


def lora_device_publish(request_dict) -> Dict:
    """ lora protocol publish """
    # TODO plugin

    record = mqtt_device_publish(request_dict)
    return record


def _emqx_device_publish(request_url: AnyStr, request_payload: Dict, control_log) -> Dict:
    with SyncHttp(auth=current_app.config['EMQ_AUTH']) as sync_http:
        response = sync_http.post(request_url, json=request_payload)
    handled_response = handle_emqx_publish_response(response)
    base_result = {
        'deviceID': request_payload['deviceID'],
        'taskID': control_log.taskID
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
        control_log.publishStatus = 0
        db.session.commit()
    return task_result
