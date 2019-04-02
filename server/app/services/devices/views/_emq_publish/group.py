from typing import AnyStr, Dict

from flask import url_for

from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_task_scheduler_response
from actor_libs.tasks.task import get_task_result
from actor_libs.types import TaskResult
from app.models import ActorTask


__all__ = ['group_publish_task_scheduler']


def group_publish_task_scheduler(request_url: AnyStr, request_payload: Dict) -> TaskResult:
    task_id = request_payload['taskID']
    task_info = {
        'taskID': task_id,
        'taskName': 'group_publish_task',
        'taskType': 1,
        'taskStatus': 1,
        'taskCount': 1,
        'taskInfo': {
            'keyword_arguments': {'request_json': request_payload},
            'arguments': []
        }
    }
    actor_task = ActorTask()
    actor_task.create(request_dict=task_info)

    query_status_url = url_for('tasks.get_task_scheduler_status')[7:]
    with SyncHttp() as sync_http:
        response = sync_http.post(request_url, json=request_payload)
    handled_response = handle_task_scheduler_response(response)

    if handled_response.get('status') == 3:
        success_result = {
            'groupID': request_payload['groupID'],
            'statusUrl': f"{query_status_url}?taskID={task_id}"
        }
        task_result = get_task_result(
            status=3, task_id=task_id, message='Group publish success',
            result=success_result
        )
    else:
        error_message = handled_response.get('error') or 'Group publish failed'
        task_result = get_task_result(
            status=4, message=error_message
        )
    return task_result
