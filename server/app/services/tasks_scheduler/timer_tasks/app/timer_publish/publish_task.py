from typing import List, Dict

from ._device import get_devices_info, build_device_publish_info, devices_publish
from ._parse import get_due_tasks
from ._utills import get_timer_tasks


__all__ = ['timer_publish_task']


async def timer_publish_task():
    due_tasks_id = await get_due_tasks()
    if not due_tasks_id:
        # not due task, return
        return {}
    publish_info = []
    due_tasks: List[Dict] = await get_timer_tasks(due_tasks_id)
    device_ids = []
    for time_task in due_tasks:
        device_ids.append(time_task.get('deviceIntID'))
    devices_info = await get_devices_info(device_ids)
    for time_task in enumerate(due_tasks):
        device_info = devices_info[time_task.get('deviceIntID')]
        _info = await build_device_publish_info(time_task, device_info)
        publish_info.append(_info)
    task_result = await devices_publish(publish_info=publish_info)
    return task_result
