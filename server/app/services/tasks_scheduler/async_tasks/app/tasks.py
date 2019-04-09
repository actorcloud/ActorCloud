from typing import List

from actor_libs.tasks.base import task
from actor_libs.types import TaskResult
from . import faust_app
from .device_publish import emqx_device_publish
from .excel_export import export_devices
from .excel_import import ImportDevices
from .group_publish import emqx_group_publish
from .timer_publish import emqx_timer_publish, update_crontab_tasks


__all__ = [
    'device_publish_task', 'group_publish_task', 'timer_publish_task',
    'excel_export_task', 'excel_import_task'
]


@task(app=faust_app, task_name='device_publish_task')
async def device_publish_task(request_json=None):
    task_result = await emqx_device_publish(request_json)
    return task_result


@task(app=faust_app, task_name='group_publish_task')
async def group_publish_task(request_json=None):
    task_result = await emqx_group_publish(request_json)
    return task_result


@task(app=faust_app, task_name='timer_publish_task')
async def timer_publish_task(due_tasks_id: List[int] = None):
    publish_payloads = await emqx_timer_publish(due_tasks_id)
    crontab_ids = []
    device_count, group_count = 0, 0
    for publish_payload in publish_payloads:
        timer_task_id = publish_payload.pop('id', 0)
        publish_type = publish_payload['publishType']
        if publish_type == 1:
            await device_publish_task.delay(request_json=publish_payload)
            device_count += 1
        elif publish_type == 2:
            await group_publish_task.delay(request_json=publish_payload)
            group_count += 1
        if publish_payload['timerType'] == 1:
            crontab_ids.append(timer_task_id)
    if crontab_ids:
        await update_crontab_tasks(crontab_ids)
    task_result = {'result': {'device': device_count, 'group': group_count}}
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
