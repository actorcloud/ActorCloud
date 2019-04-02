from collections import defaultdict
from datetime import datetime, timedelta
from random import randint

from flask import g, jsonify, request, url_for, current_app
from flask_uploads import UploadNotAllowed
from sqlalchemy import and_, desc, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from actor_libs.database.orm import db
from actor_libs.decorators import limit_upload_file
from actor_libs.errors import (
    APIException, DataExisted, DataNotFound, ParameterInvalid,
    ReferencedError, ResourceLimited, InternalError
)
from actor_libs.cache import Cache
from actor_libs.http_tools.responses import handle_task_scheduler_response
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.utils import generate_uuid, validate_time_period_query, get_delete_ids
from app import auth
from app import excels
from app.models import (
    Application, Cert, CertAuth, DataStream, Device, DeviceConnectLog,
    DeviceEvent, DictCode, Gateway, Group, MqttAcl, MqttSub, Policy, Product,
    ProductGroupSub, User, Client, DeviceControlLog,
    Tag, ActorTask, ClientTag
)
from . import bp
from .security import create_cn, generate_cert_file
from ..schemas import (
    DeviceIdsSchema, DeviceLocationSchema, DeviceSchema,
    DeviceUpdateSchema, MqttSubSchema
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

    query = tag_query(query)

    code_list = ['authType', 'deviceType', 'deviceStatus', 'cloudProtocol']
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

    code_list = ['authType', 'deviceType', 'deviceStatus', 'cloudProtocol']
    record = query.to_dict(code_list=code_list)
    record.update({
        'connectedAt': None, 'clientIP': None,
        'keepAlive': None, 'gatewayName': None
    })

    # If device is online,query connect time and IP
    if record.get('deviceStatus') == 1:
        connect_log = DeviceConnectLog.query \
            .filter(DeviceConnectLog.connectStatus == 1,
                    DeviceConnectLog.deviceID == record.get('deviceID'),
                    DeviceConnectLog.tenantID == g.tenant_uid) \
            .order_by(desc(DeviceConnectLog.createAt)).first()
        if connect_log:
            record['connectedAt'] = connect_log.createAt.strftime("%Y-%m-%d %H:%M:%S")
            record['clientIP'] = connect_log.IP
            record['keepAlive'] = connect_log.keepAlive

    # If device is terminal and upLink system is gateway,query gateway name
    if record['deviceType'] == 1 and record['upLinkSystem'] == 2:
        gateway = db.session.query(Gateway.deviceName) \
            .filter(Gateway.tenantID == g.tenant_uid,
                    Gateway.id == record['gateway']) \
            .first()
        if gateway:
            record['gatewayName'] = gateway.deviceName
    tags = []
    tags_index = []
    query_tags = Tag.query \
        .join(ClientTag) \
        .filter(ClientTag.c.deviceIntID == device_id) \
        .all()
    for tag in query_tags:
        tags.append(tag.tagID)
        tags_index.append({'value': tag.id, 'label': tag.tagName})
    record['tags'] = tags
    record['tagIndex'] = tags_index
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


@bp.route('/device_connect_logs')
@auth.login_required
def list_device_connect_logs():
    query = DeviceConnectLog.query \
        .join(Client, and_(Client.deviceID == DeviceConnectLog.deviceID,
                           Client.tenantID == DeviceConnectLog.tenantID)) \
        .with_entities(DeviceConnectLog, Client.deviceName)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Device.productID.in_(product_ids))
    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Client.deviceName.ilike(u'%{0}%'.format(device_name)))

    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/connect_logs')
@auth.login_required
def view_device_connect_logs(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = DeviceConnectLog.query \
        .filter(DeviceConnectLog.deviceID == device.deviceID,
                DeviceConnectLog.tenantID == device.tenantID)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)


@bp.route('/device_control_logs')
@auth.login_required
def list_control_logs():
    query = DeviceControlLog.query \
        .join(User, User.id == DeviceControlLog.userIntID) \
        .join(Device, Device.id == DeviceControlLog.deviceIntID) \
        .with_entities(DeviceControlLog, Device.deviceName,
                       User.username.label('createUser'))
    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Device.productID.in_(product_ids))

    records = query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/control_logs')
@auth.login_required
def device_control_logs(device_id):
    device = Device.query.with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = DeviceControlLog.query \
        .join(User, User.id == DeviceControlLog.userIntID) \
        .with_entities(DeviceControlLog, User.username.label('createUser')) \
        .filter(DeviceControlLog.deviceIntID == device.id)
    records = query.paginate(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/device_events')
@auth.login_required
def list_device_events():
    query = DeviceEvent.query \
        .join(Client, and_(Client.deviceID == DeviceEvent.deviceID,
                           Client.tenantID == DeviceEvent.tenantID)) \
        .with_entities(DeviceEvent, Client.deviceName)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Product.productID.in_(product_ids))
    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Client.deviceName.ilike(u'%{0}%'.format(device_name)))

    records = query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/events')
@auth.login_required
def view_device_events(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id) \
        .first_or_404()
    events_query = DeviceEvent.query \
        .filter(DeviceEvent.deviceID == device.deviceID,
                DeviceEvent.tenantID == device.tenantID)

    data_type = request.args.get('dataType', type=str)
    if data_type == 'realtime':
        events_query = events_query \
            .filter(DeviceEvent.msgTime >= text("NOW() - INTERVAL '1 DAYS'"))
    elif data_type == 'history':
        start_time, end_time = validate_time_period_query()
        events_query = events_query \
            .filter(DeviceEvent.msgTime >= start_time, DeviceEvent.msgTime <= end_time)
    else:
        raise ParameterInvalid(field='dataType')
    events_query = events_query.order_by(DeviceEvent.msgTime.desc())

    records = events_query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/subscriptions')
@auth.login_required
def list_device_subs(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    sub_query = MqttSub.query.filter(MqttSub.deviceIntID == device.id)
    records = sub_query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/subscriptions', methods=['POST'])
@auth.login_required
def create_device_sub(device_id):
    request_dict = MqttSubSchema.validate_request()
    topic = request_dict.get('topic')

    device, cloud_protocol = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device, Product.cloudProtocol) \
        .filter(Device.id == device_id) \
        .first_or_404()
    if cloud_protocol != 1:
        raise ResourceLimited(field='cloudProtocol')

    client_uid = ':'.join([g.tenant_uid, device.productID, device.deviceID])
    query_mqtt_sub = db.session.query(MqttSub.clientID, MqttSub.topic) \
        .filter(MqttSub.clientID == client_uid)
    is_exist_sub = query_mqtt_sub.filter(MqttSub.topic == topic).first()
    sub_sum = query_mqtt_sub.all()
    if is_exist_sub:
        raise DataExisted(field='topic')
    if len(sub_sum) >= 10:
        raise ResourceLimited(field='topic')

    request_dict['clientID'] = client_uid
    request_dict['deviceIntID'] = device.id
    mqtt_sub = MqttSub()
    created_mqtt_sub = mqtt_sub.create(request_dict=request_dict)
    record = created_mqtt_sub.to_dict()
    return jsonify(record), 201


@bp.route('/devices/<int:device_id>/subscriptions', methods=['DELETE'])
@auth.login_required
def delete_device_sub(device_id):
    delete_ids = get_delete_ids()
    try:
        query_mqtt_sub = MqttSub.query \
            .filter(MqttSub.deviceIntID == device_id,
                    MqttSub.id.in_(set(delete_ids))) \
            .all()
        if len(delete_ids) != len(query_mqtt_sub):
            raise DataNotFound(field='url')

        for mqtt_sub in query_mqtt_sub:
            db.session.delete(mqtt_sub)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices/<int:device_id>/certs')
@auth.login_required
def list_device_certs(device_id):
    device = Device.query \
        .filter(Device.id == device_id) \
        .with_entities(Device.id) \
        .first_or_404()

    cert_query = Cert.query \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(CertAuth.deviceIntID == device.id) \
        .with_entities(Cert.id, Cert.createAt, Cert.name, Cert.enable)

    records = cert_query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/certs', methods=['POST'])
@auth.login_required
def bind_cert(device_id):
    request_dict = DeviceIdsSchema.validate_request()
    add_cert_ids = request_dict.get('ids')

    device_uid, product_uid = Device.query \
        .with_entities(Device.deviceID, Device.productID) \
        .filter(Device.id == device_id) \
        .first_or_404()
    client_uid = ':'.join([g.tenant_uid, product_uid, device_uid])

    exist_auth_certs = db.session.query(Cert.id) \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(Cert.id.in_(add_cert_ids),
                CertAuth.deviceIntID == device_id) \
        .all()
    exist_auth_cert_ids = [cert.id for cert in exist_auth_certs]

    diff_cert_ids = set(add_cert_ids).difference(set(exist_auth_cert_ids))
    diff_cert = Cert.query \
        .join(User, User.id == Cert.userIntID) \
        .filter(Cert.id.in_(diff_cert_ids),
                User.tenantID == g.tenant_uid) \
        .all()
    for cert in diff_cert:
        new_cert_auth = CertAuth(
            deviceIntID=device_id, CN=cert.CN,
            clientID=client_uid, enable=cert.enable
        )
        db.session.add(new_cert_auth)
    db.session.commit()
    return '', 201


@bp.route('/devices/<int:device_id>/certs', methods=['DELETE'])
@auth.login_required
def delete_device_certs(device_id):
    delete_ids = get_delete_ids()

    try:
        cert_auth_list = CertAuth.query \
            .join(Device, Device.id == CertAuth.deviceIntID) \
            .join(Cert, Cert.CN == CertAuth.CN) \
            .filter(Device.id == device_id,
                    Cert.id.in_(delete_ids)) \
            .all()
        if len(delete_ids) != len(cert_auth_list):
            raise DataNotFound(field='url')

        for cert_auth in cert_auth_list:
            db.session.delete(cert_auth)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices/<int:device_id>/policies')
@auth.login_required
def list_device_policies(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = Policy.query \
        .join(MqttAcl, MqttAcl.policyIntID == Policy.id) \
        .filter(MqttAcl.deviceIntID == device.id)

    records = query.pagination(code_list=['access', 'allow'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/policies', methods=['POST'])
@auth.login_required
def bind_policy(device_id):
    request_dict = DeviceIdsSchema.validate_request()
    add_policy_ids = set(request_dict.get('ids'))

    device_uid, product_uid = Device.query \
        .with_entities(Device.deviceID, Device.productID) \
        .filter(Device.id == device_id) \
        .first_or_404()

    client_uid = ':'.join([g.tenant_uid, product_uid, device_uid])

    mqtt_acl = db.session.query(MqttAcl.policyIntID) \
        .filter(MqttAcl.deviceIntID == device_id,
                MqttAcl.policyIntID.in_(add_policy_ids)) \
        .all()
    exist_acl_policy_ids = [acl.policyIntID for acl in mqtt_acl]

    diff_policy_ids = set(add_policy_ids).difference(set(exist_acl_policy_ids))
    policies = Policy.query \
        .join(User, User.id == Policy.userIntID) \
        .filter(Policy.id.in_(diff_policy_ids),
                User.tenantID == g.tenant_uid) \
        .all()

    for policy in policies:
        new_mqtt_acl = MqttAcl(
            allow=policy.allow,
            access=policy.access,
            policyIntID=policy.id,
            topic=policy.topic,
            clientID=client_uid,
            deviceIntID=device_id
        )
        db.session.add(new_mqtt_acl)
    db.session.commit()
    return '', 201


@bp.route('/devices/<int:device_id>/policies', methods=['DELETE'])
@auth.login_required
def delete_device_policies(device_id):
    delete_ids = get_delete_ids()

    try:
        mqtt_acl = MqttAcl.query \
            .filter(MqttAcl.deviceIntID == device_id,
                    MqttAcl.policyIntID.in_(delete_ids)) \
            .all()
        if len(delete_ids) != len(mqtt_acl):
            raise DataNotFound(field='url')

        for acl in mqtt_acl:
            db.session.delete(acl)
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
        response = sync_http.post(export_url, json=request_json)

    handled_response = handle_task_scheduler_response(response)
    if handled_response.get('status') == 3:
        query_status_url = url_for('tasks.get_task_scheduler_status')[7:]
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
    code_list = ['authType', 'deviceType', 'upLinkSystem']
    dict_code_object = {
        code: Cache().dict_code.get(code) for code in code_list
    }

    import_url = current_app.config.get('IMPORT_EXCEL_TASK_URL')
    task_id = generate_uuid()
    task_kwargs = {
        'filePath': file_path,
        'dictCode': dict_code_object,
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
        response = sync_http.post(import_url, json=task_kwargs)

    handled_response = handle_task_scheduler_response(response)
    if handled_response.get('status') == 3:
        query_status_url = url_for('tasks.get_task_scheduler_status')[7:]
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


def create_and_bind_cert(created_device):
    cert_name = created_device.deviceName
    if db.session.query(func.count(Cert.id)) \
            .filter(Cert.name == cert_name).scalar():
        cert_name = random_cert_name(cert_name)
    created_cn = create_cn()
    st_private_key, st_client_cert, _ = generate_cert_file(created_cn)

    cert_request_dict = {
        'name': cert_name,
        'enable': 1,
        'key': st_private_key,
        'cert': st_client_cert,
        'CN': created_cn,
        'userIntID': g.user_id
    }
    cert = Cert()
    created_cert = cert.create(cert_request_dict, commit=False)
    client_uid = ':'.join([
        created_device.tenantID, created_device.productID,
        created_device.deviceID
    ])
    cert_auth_request_dict = {
        'deviceIntID': created_device.id,
        'CN': created_cert.CN,
        'clientID': client_uid,
        'enable': created_cert.enable
    }
    cert_auth = CertAuth()
    cert_auth.create(cert_auth_request_dict, commit=False)


def random_cert_name(original_name):
    cert_name = original_name + str(randint(1, 10000))

    if db.session.query(func.count(Cert.id)) \
            .filter(Cert.name == cert_name).scalar() > 0:
        cert_name = random_cert_name(original_name)
    return cert_name


def device_product_sub(created_device, product_id):
    """
    If the product has topic subscription, insert the device to MqttSub (no commit)
    """

    client_uid = ':'.join(
        [g.tenant_uid, created_device.productID, created_device.deviceID]
    )
    product_subs = db.session \
        .query(ProductGroupSub.topic, ProductGroupSub.qos) \
        .filter(ProductGroupSub.productIntID == product_id) \
        .order_by(desc(ProductGroupSub.createAt)) \
        .limit(10) \
        .all()
    for product_sub in product_subs:
        topic, qos = product_sub
        mqtt_sub = MqttSub(
            clientID=client_uid, topic=topic,
            qos=qos, deviceIntID=created_device.id
        )
        db.session.add(mqtt_sub)


def tag_query(query):
    tag_uid = request.args.get('tagID', type=str)
    if tag_uid:
        device_query = db.session.query(ClientTag.c.deviceIntID) \
            .filter(ClientTag.c.tagID == tag_uid) \
            .all()
        filter_devices = [device[0] for device in device_query]
        query = query.filter(Device.id.in_(filter_devices))
    tag_name = request.args.get('tagName_like', type=str)
    if tag_name:
        device_query = db.session.query(ClientTag.c.deviceIntID) \
            .join(Tag, Tag.tagID == ClientTag.c.tagID) \
            .filter(Tag.tagName.ilike(f'%{tag_name}%')) \
            .all()
        filter_devices = [device[0] for device in device_query]
        query = query.filter(Device.id.in_(filter_devices))
    return query
