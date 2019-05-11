import json

from flask import jsonify, current_app

from actor_libs.emqx.publish.protocol import PROTOCOL_PUBLISH_JSON_FUNC
from actor_libs.emqx.publish.schemas import PublishSchema
from actor_libs.errors import FormInvalid
from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.tasks.task import get_task_result
from actor_libs.utils import generate_uuid
from app import auth
from app.models import Device, PublishLog
from . import bp
from ._gateway_config.neuron import neuron_publish_json


@bp.route('/device_publish', methods=['POST'])
@auth.login_required
def device_publish():
    request_dict = PublishSchema.validate_request()
    # # create publish logs
    request_dict['taskID'] = generate_uuid()
    request_dict['publishStatus'] = 1
    request_dict['payload'] = json.loads(request_dict['payload'])
    client_publish_log = PublishLog()
    created_publish_log = client_publish_log.create(request_dict)
    # get publish json of protocol
    publish_json_func = PROTOCOL_PUBLISH_JSON_FUNC.get(request_dict['protocol'])
    if not publish_json_func:
        raise FormInvalid(field='cloudProtocol')
    publish_json = publish_json_func(request_dict)
    record = _emqx_client_publish(publish_json, created_publish_log)
    return jsonify(record)


@bp.route('/sync_config', methods=['POST'])
@auth.login_required
def device_sync_config():
    request_dict = PublishSchema.validate_request()
    # # create publish logs
    request_dict['taskID'] = generate_uuid()
    request_dict['publishStatus'] = 1
    request_dict['payload'] = json.loads(request_dict['payload'])
    client_publish_log = PublishLog()
    created_publish_log = client_publish_log.create(request_dict)
    # neuron publish json
    publish_json = neuron_publish_json(request_dict)
    record = _emqx_client_publish(publish_json, created_publish_log)
    return jsonify(record)


@bp.route('/devices/<int:device_id>/publish_logs')
@auth.login_required
def view_device_publish_logs(device_id):
    device = Device.query.with_entities(Device.deviceID) \
        .filter(Device.id == device_id).first_or_404()

    query = PublishLog.query \
        .filter(PublishLog.deviceID == device.deviceID)
    records = query.pagination(code_list=['publishStatus'])
    return jsonify(records)


def _emqx_client_publish(publish_json, created_publish_log):
    emqx_pub_url = f"{current_app.config['EMQX_API']}/mqtt/publish"
    with SyncHttp(auth=current_app.config['EMQX_AUTH']) as sync_http:
        response = sync_http.post(emqx_pub_url, json=publish_json)
    handled_response = handle_emqx_publish_response(response)
    base_result = {
        'deviceID': created_publish_log.deviceID,
        'taskID': created_publish_log.taskID
    }
    if handled_response['status'] == 3:
        task_result = get_task_result(
            status=3, message='Client publish success', result=base_result
        )
    else:
        error_message = handled_response.get('error') or 'Client publish failed'
        task_result = get_task_result(
            status=4, message=error_message, result=base_result
        )
        created_publish_log.publishStatus = 0
        created_publish_log.update()
    return task_result
