from arrow import now as date_now

from actor_libs.tasks.task import get_task_result
from actor_libs.types import TaskResult
from actor_libs.utils import generate_uuid
from ._single_device import (
    insert_device_control_log, handle_lwm2m_payload, lwm2m_device_publish_info,
    mqtt_device_publish_info, single_device_publish, update_control_logs, handle_mqtt_payload
)
from .. import project_config


__all__ = ['emqx_device_publish']


async def emqx_device_publish(request_dict) -> TaskResult:
    task_id = generate_uuid()  # emqx publish taskID
    protocol = request_dict['protocol'].lower()
    request_dict['protocol'] = protocol
    request_dict['taskID'] = task_id
    request_dict['publishTime'] = date_now(tz=project_config['TIMEZONE']).naive

    if protocol == 'lwm2m':
        origin_payload, encrypt_payload = await handle_lwm2m_payload(request_dict)
        await insert_device_control_log(request_dict, origin_payload)
        publish_payload, publish_url = await lwm2m_device_publish_info(
            request_dict, encrypt_payload
        )
    else:
        if protocol == 'mqtt':
            request_dict = handle_mqtt_payload(request_dict)
        await insert_device_control_log(request_dict)
        publish_payload, publish_url = await mqtt_device_publish_info(request_dict)
    publish_result = await single_device_publish(publish_payload, publish_url)
    result = {'deviceID': request_dict['deviceID'], 'taskID': task_id}
    # 3:success 4:fail
    if publish_result.get('status') == 3:
        task_result = get_task_result(
            status=3, message='Device publish success', result=result
        )
    else:
        task_result = get_task_result(
            status=4, message='Device publish failed', result=result
        )
        await update_control_logs(task_id, 0)
    return task_result
