from flask import g, jsonify, request, url_for, current_app
from flask_uploads import UploadNotAllowed
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from actor_libs.database.orm import db
from actor_libs.decorators import limit_upload_file
from actor_libs.errors import (
    APIException, ParameterInvalid,
    ReferencedError, ResourceLimited, InternalError
)
from actor_libs.http_tools.responses import handle_task_scheduler_response
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.utils import generate_uuid, get_delete_ids
from app import auth
from app import excels
from app.models import (
    DataStream, Device, ConnectLog, Gateway, Group, Product,
    User, ActorTask, ProductSub, MqttSub, GroupClient
)
from . import bp
from .device_security import create_and_bind_cert
from ..schemas import (
    DeviceLocationSchema, DeviceSchema, DeviceUpdateSchema
)


@bp.route('/devices')
@auth.login_required
def list_devices():
    query = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device, Product.id.label('productIntID'),
                       Product.productName, Product.cloudProtocol)

    group_uid = request.args.get('groupID')
    if group_uid:
        query = query.join(Device.groups).filter_by(groupID=group_uid)
    product_name = request.args.get('productName_like')
    if product_name:
        query = query \
            .filter(Product.productName.ilike(u'%{0}%'.format(product_name)))
    group_name = request.args.get('groupName_like')
    if group_name:
        query = query.join(Device.groups) \
            .filter(Group.groupName.ilike(u'%{0}%'.format(group_name)))
    product_uid = request.args.get('productID')
    if product_uid and isinstance(product_uid, str):
        query = query.filter(Product.productID == product_uid)
    query = group_query(query)

    code_list = ['authType', 'deviceStatus', 'cloudProtocol']
    records = query.pagination(code_list=code_list)
    return jsonify(records)


@bp.route('/devices/<int:device_id>')
@auth.login_required
def view_device(device_id):
    parent_device = aliased(Device)
    query = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .outerjoin(parent_device, parent_device.id == Device.parentDevice) \
        .with_entities(Device, User.username.label('createUser'),
                       Product.cloudProtocol, Product.productName,
                       Product.id.label('productIntID'),
                       parent_device.deviceName.label('parentDeviceName')) \
        .filter(Device.id == device_id)

    code_list = ['authType', 'deviceStatus', 'cloudProtocol']
    record = query.to_dict(code_list=code_list)
    record.update({
        'connectedAt': None, 'clientIP': None,
        'keepAlive': None, 'gatewayName': None
    })

    # If device is online,query connect time and IP
    if record.get('deviceStatus') == 1:
        connect_log = ConnectLog.query \
            .filter(ConnectLog.connectStatus == 1,
                    ConnectLog.deviceID == record.get('deviceID'),
                    ConnectLog.tenantID == g.tenant_uid) \
            .order_by(desc(ConnectLog.msgTime)).first()
        if connect_log:
            record['msgTime'] = connect_log.msgTime.strftime("%Y-%m-%d %H:%M:%S")
            record['clientIP'] = connect_log.IP
            record['keepAlive'] = connect_log.keepAlive

    # If client is devices and upLink system is gateway, query gateway name
    if record['clientType'] == 1 and record['upLinkSystem'] == 2:
        gateway = db.session.query(Gateway.deviceName) \
            .filter(Gateway.tenantID == g.tenant_uid,
                    Gateway.id == record['gateway']) \
            .first()
        if gateway:
            record['gatewayName'] = gateway.deviceName
    groups = []
    groups_index = []
    query_groups = Group.query.join(GroupClient) \
        .filter(GroupClient.c.clientIntID == device_id).all()
    for group in query_groups:
        groups.append(group.groupID)
        groups_index.append({'value': group.id, 'label': group.groupName})
    record['groups'] = groups
    record['groupsIndex'] = groups_index
    return jsonify(record)


@bp.route('/devices', methods=['POST'])
@auth.login_required
def create_device():
    request_dict = DeviceSchema.validate_request()
    request_dict['userIntID'] = g.user_id
    request_dict['tenantID'] = g.tenant_uid

    device = Device()
    created_device = device.create(request_dict, commit=False)
    try:
        if created_device.authType == 2 and request_dict.get('autoCreateCert') == 1:
            create_and_bind_cert(created_device)
        device_product_sub(
            created_device=created_device, product_id=request_dict['productIntID']
        )
    except Exception as e_msg:
        raise InternalError(field=e_msg)
    db.session.commit()
    record = created_device.to_dict()
    record['cloudProtocol'] = request_dict['cloudProtocol']
    return jsonify(record), 201


@bp.route('/devices/<int:device_id>', methods=['PUT'])
@auth.login_required
def update_device(device_id):
    device = Device.query.filter(Device.id == device_id).first_or_404()
    request_dict = DeviceUpdateSchema.validate_request(obj=device)
    updated_device = device.update(request_dict)
    record = updated_device.to_dict()
    record['cloudProtocol'] = request_dict['cloudProtocol']
    return jsonify(record)


@bp.route('/devices', methods=['DELETE'])
@auth.login_required
def delete_device():
    delete_ids = get_delete_ids()
    parent_device_ids = db.session.query(func.count(Device.id)) \
        .filter(Device.parentDevice.in_(delete_ids)) \
        .scalar()
    if parent_device_ids != 0:
        raise ReferencedError(field='parentDevice')
    query_results = Device.query.filter(Device.id.in_(delete_ids)).many()
    try:
        for device in query_results:
            db.session.delete(device)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices/<int:device_id>/location', methods=['PUT'])
@auth.login_required
def update_device_location(device_id):
    device = Device.query.filter(Device.id == device_id).first_or_404()

    request_dict = DeviceLocationSchema.validate_request()
    updated_device = device.update(request_dict)
    record = {
        'longitude': updated_device.longitude,
        'latitude': updated_device.latitude,
        'location': updated_device.location
    }
    return jsonify(record)


@bp.route('/devices/<int:device_id>/stream_points')
@auth.login_required()
def device_stream_point(device_id):
    """
    Return data_streams and data_points of device when publish
    """

    device = Device.query.filter(Device.id == device_id).first_or_404()
    stream_id = request.args.get('dataStreamIntID')
    try:
        stream_id = int(stream_id)
    except Exception:
        raise ParameterInvalid(field='dataStreamIntID')
    data_stream = DataStream.query \
        .filter(DataStream.productID == device.productID) \
        .filter(DataStream.id == stream_id) \
        .first()
    record = dict()
    record['streamName'] = data_stream.streamName
    record['topic'] = data_stream.topic
    record['dataPoints'] = []
    stream_points = data_stream.dataPoints
    for stream_point in stream_points:
        data_point = stream_point.dataPoint
        point_dict = dict()
        point_dict['dataPointName'] = data_point.dataPointName
        point_dict['dataPointID'] = data_point.dataPointID
        point_dict['pointDataType'] = data_point.pointDataType
        point_dict['enum'] = data_point.enum
        point_dict['value'] = ''
        record['dataPoints'].append(point_dict)

    return jsonify(record)


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


def group_query(query):
    group_uid = request.args.get('groupID', type=str)
    if group_uid:
        filter_devices = db.session.query(GroupClient.c.clientIntID) \
            .filter(GroupClient.c.groupID == group_uid) \
            .all()
        query = query.filter(Device.id.in_(filter_devices))
    group_name = request.args.get('groupName_like', type=str)
    if group_name:
        filter_devices = db.session.query(GroupClient.c.clientIntID) \
            .join(Group, Group.groupID == GroupClient.c.groupID) \
            .filter(Group.groupName.ilike(f'%{group_name}%')) \
            .all()
        query = query.filter(Device.id.in_(filter_devices))
    return query


def device_product_sub(created_device, product_id):
    """
    If the product has topic subscription, insert the device to MqttSub (no commit)
    """

    client_uid = ':'.join(
        [g.tenant_uid, created_device.productID, created_device.deviceID]
    )
    product_subs = db.session \
        .query(ProductSub.topic, ProductSub.qos) \
        .filter(ProductSub.productIntID == product_id) \
        .order_by(desc(ProductSub.createAt)) \
        .limit(10).all()
    for product_sub in product_subs:
        topic, qos = product_sub
        mqtt_sub = MqttSub(
            clientID=client_uid, topic=topic,
            qos=qos, deviceIntID=created_device.id
        )
        db.session.add(mqtt_sub)
