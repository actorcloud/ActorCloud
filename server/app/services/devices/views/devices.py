from typing import Tuple

from flask import request, jsonify, url_for, current_app, g
from flask_uploads import UploadNotAllowed
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.decorators import limit_upload_file
from actor_libs.errors import ReferencedError, FormInvalid, ResourceLimited, APIException
from actor_libs.http_tools.responses import handle_task_scheduler_response
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.types.orm import BaseQueryT, BaseModelT
from actor_libs.utils import get_delete_ids, generate_uuid
from app import auth, excels
from app.models import Device, Product, EndDevice, Gateway, User, ActorTask
from app.schemas import EndDeviceSchema, GatewaySchema
from . import bp


@bp.route('/devices')
@auth.login_required
def list_devices():
    query = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device, Product.productName,
                       Product.id.label('productIntID'),
                       Product.cloudProtocol, Product.gatewayProtocol)
    query = device_request_args_filter(query)
    code_list = ['authType', 'deviceStatus', 'cloudProtocol', 'gatewayProtocol']
    records = query.pagination(code_list=code_list)
    return jsonify(records)


@bp.route('/devices/<int:device_id>')
@auth.login_required
def view_device(device_id):
    code_list = ['authType', 'deviceStatus', 'cloudProtocol', 'gatewayProtocol']
    record = Device.query.join(User, User.id == Device.userIntID) \
        .join(Product, Product.productID == Device.productID) \
        .filter(Device.id == device_id) \
        .with_entities(Device, Product.id.label('productIntID'),
                       Product.productID,
                       Product.productName,
                       Product.cloudProtocol,
                       Product.gatewayProtocol,
                       User.username.label('createUser')) \
        .to_dict(code_list=code_list)
    return jsonify(record)


@bp.route('/devices', methods=['POST'])
@auth.login_required
def create_device():
    _, model = device_query_object()
    if model == EndDevice:
        request_dict = EndDeviceSchema.validate_request()
        device = EndDevice(deviceType=1)
    else:
        request_dict = GatewaySchema.validate_request()
        device = Gateway(deviceType=2)
    created_device = device.create(request_dict)
    record = created_device.to_dict()
    return jsonify(record), 201


@bp.route('/devices/<int:device_id>', methods=['PUT'])
@auth.login_required
def update_device(device_id):
    query, model = device_query_object()
    device = query.filter(model.id == device_id).first_or_404()
    if model == EndDevice:
        request_dict = EndDeviceSchema.validate_request(obj=device)
    else:
        request_dict = GatewaySchema.validate_request(obj=device)
    updated_device = device.update(request_dict)
    record = updated_device.to_dict()
    return jsonify(record), 201


@bp.route('/devices', methods=['DELETE'])
@auth.login_required
def delete_device():
    delete_ids = get_delete_ids()
    # check endDevice under the delete endDevice
    parent_device = db.session.query(db.func.count(EndDevice.id)) \
        .filter(EndDevice.parentDevice.in_(delete_ids)) \
        .scalar()
    if parent_device > 0:
        raise ReferencedError(field='parentDevice')
    # check endDevice under the delete gateway
    gateway_device = db.session.query(db.func.count(EndDevice.id)) \
        .filter(EndDevice.gateway.in_(delete_ids)) \
        .scalar()
    if gateway_device > 0:
        raise ReferencedError(field='endDevice')
    query_results = Device.query.filter(Device.id.in_(delete_ids)).many()
    try:
        for device in query_results:
            db.session.delete(device)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices_export')
@auth.login_required
def export_devices():
    device_count = db.session.query(func.count(Device.id)) \
        .filter(Device.tenantID == g.tenant_uid).scalar()
    if device_count and device_count > 10000:
        raise ResourceLimited(field='devices')
    export_url = current_app.config.get('EXPORT_EXCEL_TASK_URL')
    task_id = generate_uuid()
    request_json = {
        'tenantID': g.tenant_uid,
        'taskID': task_id
    }
    task_info = {
        'taskID': task_id,
        'taskName': 'excel_export_task',
        'taskType': 1,
        'taskStatus': 1,
        'taskCount': 1,
        'taskInfo': {
            'keyword_arguments': {
                'request_json': request_json
            },
            'arguments': []
        }
    }

    actor_task = ActorTask()
    actor_task.create(request_dict=task_info)
    with SyncHttp() as sync_http:
        headers = {
            'content-type': 'application/json',
            'Accept-Language': g.language
        }
        response = sync_http.post(export_url, json=request_json, headers=headers)
    handled_response = handle_task_scheduler_response(response)
    if handled_response.get('status') == 3:
        query_status_url = url_for('base.get_task_scheduler_status')[7:]
        record = {
            'status': 3,
            'taskID': task_id,
            'message': 'Devices export is in progress',
            'result': {
                'statusUrl': f"{query_status_url}?taskID={task_id}"
            }
        }
    else:
        record = {
            'status': 4,
            'message': handled_response.get('error') or 'Devices export failed',
        }
    return jsonify(record)


@bp.route('/devices_import', methods=['POST'])
@auth.login_required
@limit_upload_file(size=1048576)
def devices_import():
    try:
        file_prefix = 'device_import_' + g.tenant_uid
        file_name = excels.save(request.files['file'], name=file_prefix + '.')
    except UploadNotAllowed:
        error = {'Upload': 'Upload file format error'}
        raise APIException(errors=error)
    file_path = excels.path(file_name)
    import_url = current_app.config.get('IMPORT_EXCEL_TASK_URL')
    task_id = generate_uuid()
    task_kwargs = {
        'filePath': file_path,
        'tenantID': g.tenant_uid,
        'userIntID': g.user_id,
        'taskID': task_id
    }

    task_info = {
        'taskID': task_id,
        'taskName': 'excel_import_task',
        'taskType': 1,
        'taskStatus': 1,
        'taskCount': 1,
        'taskInfo': {
            'keyword_arguments': {
                'request_json': task_kwargs
            },
            'arguments': []
        }
    }
    actor_task = ActorTask()
    actor_task.create(request_dict=task_info)
    with SyncHttp() as sync_http:
        headers = {
            'content-type': 'application/json',
            'Accept-Language': g.language
        }
        response = sync_http.post(import_url, json=task_kwargs, headers=headers)

    handled_response = handle_task_scheduler_response(response)
    if handled_response.get('status') == 3:
        query_status_url = url_for('base.get_task_scheduler_status')[7:]
        record = {
            'status': 3,
            'taskID': task_id,
            'message': 'Devices import is in progress',
            'result': {
                'statusUrl': f"{query_status_url}?taskID={task_id}"
            }
        }
    else:
        record = {
            'status': 4,
            'message': handled_response.get('error') or 'Devices import failed',
        }
    return jsonify(record)


def device_query_object() -> Tuple[BaseQueryT, BaseModelT]:
    device_type = request.args.get('deviceType', type=int)
    if request.method in ('PUT', 'POST'):
        request_dict = request.get_json() or {}
        device_type = request_dict.get('deviceType')
        if device_type not in [1, 2]:
            raise FormInvalid(field='deviceType')
    if device_type == 1:
        query, model = EndDevice.query, EndDevice
    elif device_type == 2:
        query, model = Gateway.query, Gateway
    else:
        query, model = Device.query, Device
    return query, model


def device_request_args_filter(query: BaseQueryT) -> BaseQueryT:
    request_args = request.args
    if request_args.get('productName', type=str):
        query = query.filter(Product.productName.ilike(f"{request_args['productName']}"))
    elif request_args.get('cloudProtocol', type=int):
        query = query.filter(Product.cloudProtocol == request_args['cloudProtocol'])
    elif request_args.get('gatewayProtocol', type=int):
        query = query.filter(Product.gatewayProtocol == request_args['gatewayProtocol'])
    elif request_args.get('parentDevice', type=int):
        # sub devices list
        query = query.join(EndDevice, EndDevice.id == Device.id) \
            .filter(EndDevice.parentDevice == request_args['parentDevice'])
    elif request_args.get('gateway', type=int):
        # gateway devices list
        query = query.join(EndDevice, EndDevice.id == Device.id) \
            .filter(EndDevice.gateway == request_args['gateway'])
    return query
