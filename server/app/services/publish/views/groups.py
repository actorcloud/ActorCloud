from flask import jsonify, current_app

from actor_libs.utils import generate_uuid
from app import auth
from app.models import User, Group, GroupPublishLog
from app.schemas import GroupPublishSchema
from . import bp
from ._libs import group_publish_task_scheduler


@bp.route('/group_publish', methods=['POST'])
@auth.login_required
def group_publish():
    """
    record = {'status': , 'taskID': xx, 'result': {}}
    """

    task_id = generate_uuid()  # actor_task:taskID
    request_dict = GroupPublishSchema.validate_request()
    request_dict['taskID'] = task_id
    task_schedule_url = current_app.config['PUBLISH_TASK_URL']
    if request_dict['protocol'] == 'lwm2m':
        record = {
            'status': 4, 'message': "Group publish doesn't support lwm2m yet",
            'result': {'groupID': request_dict['groupID']}
        }
    else:
        record = group_publish_task_scheduler(
            request_url=task_schedule_url,
            request_payload=request_dict
        )
    return jsonify(record)


@bp.route('/groups/<int:group_id>/publish_logs')
@auth.login_required
def view_group_publish_logs(group_id):
    group = Group.query.with_entities(Group.groupID) \
        .filter(Group.id == group_id).first_or_404()

    query = GroupPublishLog.query \
        .join(User, User.id == GroupPublishLog.userIntID) \
        .with_entities(GroupPublishLog, User.username.label('createUser')) \
        .filter(GroupPublishLog.groupID == group.groupID)
    records = query.pagination(code_list=['publishStatus', 'controlType'])
    return jsonify(records)
