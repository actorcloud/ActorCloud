from datetime import datetime

from flask import jsonify, request, current_app
from sqlalchemy.orm.attributes import flag_modified

from actor_libs.database.orm import db
from actor_libs.errors import APIException, FormInvalid
from actor_libs.utils import generate_uuid
from app import auth
from app.models import (
    DeviceControlLog, Lwm2mItem, Lwm2mInstanceItem
)
from . import bp
from ._emq_publish import DEVICE_PUBLISH_FUNC
from ._emq_publish.group import (
    group_publish_task_scheduler
)
from ..schemas import (
    DevicePublishSchema, GroupPublishSchema
)


@bp.route('/device_publish', methods=['POST'])
@auth.login_required
def device_publish():
    request_dict = DevicePublishSchema.validate_request()
    request_dict['taskID'] = generate_uuid()
    request_dict['publishStatus'] = 1
    protocol = request_dict['protocol']
    device_publish_func = DEVICE_PUBLISH_FUNC.get(protocol)
    if not device_publish_func:
        device_publish_func = DEVICE_PUBLISH_FUNC['mqtt']
    record = device_publish_func(request_dict)
    return jsonify(record)


@bp.route('/group_publish', methods=['POST'])
@auth.login_required
def group_publish():
    """
    record = {'status': , 'taskID': xx, 'result': {}}
    """

    task_id = generate_uuid()  # actor_task:taskID
    request_dict = GroupPublishSchema.validate_request()
    request_dict['taskID'] = task_id
    task_schedule_url = current_app.config['TASK_SCHEDULER_URL']
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


@bp.route('/device_publish/mqtt_callback', methods=['POST'])
def device_publish_mqtt_callback():
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    if not isinstance(request_dict.get('task_id'), str):
        raise FormInvalid(field='task_id')
    control_log = DeviceControlLog.query \
        .filter(DeviceControlLog.taskID == request_dict.get('task_id')) \
        .first_or_404()
    control_log.publishStatus = 2
    db.session.commit()
    return 'success'


@bp.route('/device_publish/lwm2m_callback', methods=['POST'])
def device_publish_lwm2m_callback():
    """
    {
        "taskID": "xxx",
        "status": 4,
        "message": "",
        "content": [
            {"name": "aaa","path": "/3/0/1","value": "xxx"},
            {"name": "bbb","path": "/3/1/2","value": "xxx"}],
        "tenantID": "",
        "productID": "",
        "deviceID": ""
    }
    """
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    current_app.logger.debug(request_dict)
    if not isinstance(request_dict.get('taskID'), str):
        raise FormInvalid(field='taskID')
    control_log = DeviceControlLog.query \
        .filter(DeviceControlLog.taskID == request_dict.get('taskID')) \
        .first_or_404()
    control_log.publishStatus = request_dict.get('status')
    item = Lwm2mItem.query \
        .join(Lwm2mInstanceItem, Lwm2mInstanceItem.itemIntID == Lwm2mItem.id) \
        .filter(Lwm2mInstanceItem.path == control_log.path) \
        .first_or_404()
    if control_log.controlType == 2:
        content = request_dict.get('content')
        value = content[0].get('value')
        if item.itemType == 'Time':
            value = datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
        control_log.payload['value'] = value
        flag_modified(control_log, 'payload')
    db.session.commit()
    return 'success'
