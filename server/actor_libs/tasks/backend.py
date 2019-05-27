import json
from datetime import datetime
from typing import Dict, AnyStr

from mode.utils.objects import qualname

from actor_libs.database.async_db import db
from actor_libs.types import TaskResult
from actor_libs.utils import generate_uuid
from ._sql_statement import update_task_sql, insert_task_sql


__all__ = ['store_task', 'update_task', 'get_task_result']


class ActorTask:
    createAt: datetime = None
    updateAt: datetime = None
    taskName: AnyStr
    taskID: AnyStr
    taskStatus: int
    taskInfo: Dict = None
    taskResult: Dict = None

    def to_dict(self):
        _dict = {
            'createAt': self.createAt,
            'updateAt': self.updateAt,
            'taskName': self.taskName,
            'taskID': self.taskID,
            'taskStatus': self.taskStatus,
            'taskInfo': self.taskInfo,
            'taskResult': self.taskResult,
        }
        return _dict


async def store_task(func, *, func_args=None, func_kwargs=None):
    func_path = qualname(func)  # import_module
    task = ActorTask()
    task.taskStatus = 1
    task.createAt = datetime.now()
    task.taskID = generate_uuid()
    task.taskName = func_path.split('.')[-1]
    task_info = {
        'path': func_path,
        'args': func_args if func_args else [],
        'kwargs': func_kwargs if func_kwargs else {}
    }
    task.taskInfo = json.dumps(task_info)
    _actor_task = task.to_dict()
    await db.execute(
        insert_task_sql.format(**_actor_task)
    )
    return task.taskID


async def update_task(task_id, update_dict: Dict = None) -> bool:
    if not update_dict:
        update_dict = {}
    task_update_dict = {
        'taskID': task_id,
        'updateAt': datetime.now(),
        'taskStatus': update_dict['status'] if update_dict.get('status') else 2,
        'taskProgress': update_dict['progress'] if update_dict.get('progress') else 0,
        'taskResult': json.dumps(update_dict['result']) if update_dict.get('result') else 'NULL'
    }
    update_sql = update_task_sql.format(**task_update_dict)
    execute_result = await db.execute(update_sql)
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
