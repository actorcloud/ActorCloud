import json
from typing import Dict, AnyStr

from actor_libs.types import TaskResult
from ._sql_statement import update_task_sql, insert_task_sql
from datetime import datetime
from actor_libs.database.async_db import db


__all__ = [
    'store_task', 'update_task', 'handle_task_result', 'get_task_result'
]


class TaskInfo:
    createAt: datetime = None
    updateAt: datetime = None
    taskName: AnyStr
    taskID: AnyStr
    taskStatus: int
    taskInfo: Dict = {}
    taskResult: Dict = {}

    def to_dict(self):
        _dict = {
            'createAt': self.createAt,
            'updateAt': self.updateAt,
            'taskName': self.createAt,
            'taskID': self.taskID,
            'taskStatus': self.taskStatus,
            'taskInfo': self.taskInfo,
            'taskResult': self.taskResult,
        }
        return _dict


async def store_task(postgres, task_info) -> bool:
    dump_json = json.dumps({
        'arguments': task_info.arguments,
        'keyword_arguments': task_info.keyword_arguments
    })
    _actor_task = {
        'createAt': task_info.createAt,
        'taskID': task_info.taskID,
        'taskStatus': task_info.taskStatus,
        'taskName': task_info.taskName,
        'taskInfo': dump_json
    }
    execute_status = await postgres.execute(
        insert_task_sql.format(**_actor_task))
    return execute_status


async def update_task(postgres, update_dict: Dict) -> bool:
    update_sql = update_task_sql.format(**update_dict)
    execute_result = await postgres.execute(update_sql)
    return execute_result


def get_task_result(status: int,
                    message: AnyStr,
                    result: Dict = None,
                    progress: int = None,
                    task_id: AnyStr = None,
                    **kwargs) -> TaskResult:
    if status == 1:
        task_result = {
            'status': 1,
            'progress': 0,
            'message': message if message else 'Task pending'
        }
    elif status == 2:
        task_result = {
            'status': 2,
            'progress': progress if progress else 50,
            'message': message if message else 'Task processing',
        }
    elif status == 3:
        task_result = {
            'status': 3,
            'progress': 100,
            'message': message if message else 'Task success',
        }
    elif status == 4:
        task_result = {
            'status': 4,
            'progress': 100,
            'message': message if message else 'Task failed',
        }
    elif status == 5:
        task_result = {
            'status': 5,
            'progress': 1,
            'count': kwargs['count'] if kwargs.get('count') else 1,
            'message': message if message else 'Task retrying',
        }
    else:
        task_result = {}
    if task_id:
        task_result['taskID'] = task_id
    if result:
        task_result['result'] = result
    task_result.update(kwargs)
    return task_result


async def handle_task_result(postgres, actor_task, date_now) -> None:
    task_id = actor_task.taskID
    try:
        task_result: TaskResult = await actor_task()
    except Exception as e:
        task_result = {
            'status': 4,
            'progress': 0,
            'message': e,
        }
    if task_result.get('task_ignore'):
        return
    message = task_result.get('message', '')
    result = task_result.get('result', {})
    result['message'] = message
    result['code'] = task_result.get('code')
    update_dict = {
        'updateAt': date_now,
        'taskStatus': task_result.get('status', 4),
        'taskProgress': task_result.get('progress', 100),
        'taskResult': json.dumps(result),
        'taskID': task_id
    }
    await update_task(postgres, update_dict)
