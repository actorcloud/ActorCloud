from typing import List

from actor_libs.tasks.base import task
from actor_libs.types import TaskResult
from . import faust_app
from .device_publish import device_publish
from .excel_export import export_devices
from .excel_import import ImportDevices
from .timer_publish import timer_publish, update_crontab_tasks


__all__ = [
    'device_publish_task', 'timer_publish_task',
    'excel_export_task', 'excel_import_task'
]


@task(app=faust_app, task_name='device_publish_task')
async def device_publish_task(request_json=None):
    task_result = await device_publish(request_json)
    return task_result


@task(app=faust_app, task_name='timer_publish_task')
async def timer_publish_task(due_tasks_id: List[int] = None):
    publish_info = await timer_publish(due_tasks_id)
    crontab_ids = []
    device_count = 0
    for _info in publish_info:
        await device_publish_task.delay(request_json=_info)
        if _info['timerType'] == 1:
            crontab_ids.append(_info['timerTaskID'])
    if crontab_ids:
        await update_crontab_tasks(crontab_ids)
    task_result = {'result': {'device': device_count}}
    return task_result


@task(app=faust_app, task_name='excel_import_task')
async def excel_import_task(request_json=None) -> TaskResult:
    import_devices = ImportDevices(task_kwargs=request_json)
    task_result = await import_devices.import_excel()
    return task_result


@task(app=faust_app, task_name='excel_export_task')
async def excel_export_task(request_json=None) -> TaskResult:
    tenant_uid = request_json.get('tenantID')
    task_result = await export_devices(request_json.get('language'), tenant_uid)
    return task_result
