from typing import AnyStr, List, Dict

from ._device import handle_device_timer_task, get_ids_device_info
from ._group import handle_group_timer_task, get_uids_group_info
from ._timer import get_timer_tasks


async def emqx_timer_publish(due_tasks_id: List[int]):
    due_tasks: List[Dict] = await get_timer_tasks(due_tasks_id)

    device_ids, group_ids = [], []
    device_append, group_append = device_ids.append, group_ids.append
    for index, time_task in enumerate(due_tasks):
        publish_type = time_task.get('publishType')
        if publish_type == 1 and time_task.get('deviceIntID'):
            device_append(time_task['deviceIntID'])
        elif publish_type == 2 and time_task.get('groupID'):
            group_append(time_task['groupID'])
        else:
            del due_tasks[index]
    device_ids_info = await get_ids_device_info(device_ids)
    group_ids_info = await get_uids_group_info(group_ids)

    for index, due_task in enumerate(due_tasks):
        publish_type = due_task.get('publishType')
        device_id: int = due_task.get('deviceIntID')
        group_uid: AnyStr = due_task.get('groupID')
        if publish_type == 1 and device_ids_info.get(device_id):
            device_info = device_ids_info[device_id]
            await handle_device_timer_task(due_task, device_info)
        elif publish_type == 2 and group_ids_info.get(group_uid):
            group_info = group_ids_info[group_uid]
            await handle_group_timer_task(due_task, group_info)
        else:
            del due_tasks[index]
    return due_tasks
