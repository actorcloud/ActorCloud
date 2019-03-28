from flask import request, jsonify

from app import auth
from actor_libs.errors import ParameterInvalid
from app.models import ActorTask
from . import bp


@bp.route('/task_status')
@auth.login_required(permission_required=False)
def get_task_scheduler_status():
    task_scheduler_id = request.args.get('taskID', type=str)
    if not task_scheduler_id:
        raise ParameterInvalid(field='taskID')
    query_task = ActorTask.query \
        .filter(ActorTask.taskID == task_scheduler_id) \
        .first_or_404()
    result = query_task.taskResult if query_task.taskResult else {}
    message = result.pop('message', '')
    record = {
        'status': query_task.taskStatus,
        'progress': query_task.taskProgress,
        'message': message,
        'taskID': query_task.taskID,
        'result': result,
    }
    return jsonify(record)
