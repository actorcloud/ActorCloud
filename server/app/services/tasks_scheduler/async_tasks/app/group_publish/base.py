from arrow import now as date_now

from actor_libs.types import TaskResult
from actor_libs.utils import generate_uuid
from ._group_devices import (
    insert_group_control_log, mqtt_group_publish_info, update_group_control_log, group_emqx_publish
)
from .. import project_config


async def emqx_group_publish(request_dict) -> TaskResult:
    task_id = generate_uuid()  # emqx publish taskID
    protocol = request_dict.get('protocol').lower()
    request_dict['protocol'] = protocol
    request_dict['taskID'] = task_id
    request_dict['publishTime'] = date_now(tz=project_config['TIMEZONE']).naive

    if protocol == 'lwm2m':
        task_result = {
            'status': 4,
            'progress': 100,
            'message': 'Group publish nonsupport lwm2m',
            'result': {
                'groupID': request_dict['groupID'],
                'taskID': task_id
            }
        }
    else:
        group_control_log_id = await insert_group_control_log(request_dict)
        group_devices_publish, publish_url = await mqtt_group_publish_info(
            request_dict, group_control_log_id)
        task_result = await group_emqx_publish(group_devices_publish,
                                               publish_url)
        if task_result['status'] == 4:
            await update_group_control_log(group_control_log_id)
    return task_result
