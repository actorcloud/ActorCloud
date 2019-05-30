import json
from datetime import datetime

from flask import jsonify, request, current_app
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound, AuthFailed
from actor_libs.http_tools import SyncHttp
from app.models import Product, Device, DictCode, Cert, ConnectLog, CertDevice, PublishLog
from . import bp


@bp.route('/emqx/auth', methods=['POST'])
def device_auth():
    request_form = request.form
    device_uid = request_form.get('device_id')
    cn = request_form.get('cn')
    connect_date = datetime.now()
    # query device info
    query = db.session \
        .query(Device, func.lower(DictCode.enLabel).label('protocol')) \
        .join(Product, Product.productID == Device.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Device.deviceID == device_uid, Device.blocked == 0,
                DictCode.code == 'cloudProtocol')
    if cn is None or cn == 'undefined':
        # token auth
        query = query.filter(Device.authType == 1)
    else:
        # cert auth
        query = query \
            .join(CertDevice, CertDevice.c.deviceIntID == Device.id) \
            .join(Cert, Cert.id == CertDevice.c.certIntID) \
            .filter(Device.authType == 2, Cert.CN == cn, Cert.enable == 1)
    device_info = query.first()
    if not device_info:
        raise AuthFailed(field='device')
    device, protocol = device_info
    auth_status = _validate_connect_auth(device, protocol, request_form)
    # insert connect_logs
    connect_dict = {
        'IP': request_form.get('ip'),
        'msgTime': connect_date,
        'deviceID': device.deviceID,
        'tenantID': device.tenantID
    }
    connect_log = ConnectLog()
    if auth_status:
        connect_dict['connectStatus'] = 1
        device.deviceStatus = 1
        device.lastConnection = connect_date
        record = {
            'mountpoint': f'/{protocol}/{device.tenantID}/{device.productID}/{device.deviceID}/'
        }
        code = 200
    else:
        connect_dict['connectStatus'] = 2
        record, code = {'status': 401}, 401
    connect_log.create(request_dict=connect_dict)
    return jsonify(record), code


@bp.route('/emqx/callback', methods=['POST'])
def backend_callback():
    request_dict = request.get_json()
    request_dict['callback_date'] = datetime.now()
    if not request_dict:
        raise DataNotFound()
    callback_action = request_dict.get('action')
    handle_action_funcs = {
        'client_connected': client_connected_callback,
        'client_disconnected': client_disconnected_callback,
        'message_acked': message_acked_callback,
    }
    if not handle_action_funcs.get(callback_action):
        raise DataNotFound()
    handle_action = handle_action_funcs[callback_action]
    handle_action(request_dict)
    return '', 201


def _validate_connect_auth(device, protocol, request_form) -> bool:
    if protocol == 'lwm2m' or device.authType == 2:
        auth_status = True
    elif all([device.authType == 1,
              device.deviceUsername == request_form.get('username'),
              device.token == request_form.get('password')]):
        auth_status = True
    else:
        auth_status = False
    return auth_status


def client_disconnected_callback(request_dict) -> None:
    device_id = request_dict.get('client_id')
    if not device_id:
        return
    device = Device.query.filter(Device.deviceID == device_id).first()
    if not device:
        return
    connect_dict = {
        'msgTime': request_dict['callback_date'],
        'deviceID': device.deviceID,
        'tenantID': device.tenantID,
        'connectStatus': 0
    }
    connect_log = ConnectLog()
    connect_log.create(request_dict=connect_dict, commit=False)
    device.deviceStatus = 0
    device.update()


def client_connected_callback(request_dict) -> None:
    """ Device connected subscribe inbox topic """

    device_id = request_dict.get('client_id')
    if not device_id:
        return
    device = db.session \
        .query(Device.tenantID, Device.productID,
               Device.deviceID, func.lower(DictCode.enLabel).label('protocol')) \
        .join(Product, Product.productID == Device.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Device.deviceID == device_id, DictCode.code == 'cloudProtocol') \
        .first()
    if not device or device.protocol == 'lwm2m':
        # if device protocol is lwm2m pass
        return

    auto_sub_topic = (
        f"/{device.protocol}/{device.tenantID}"
        f"/{device.productID}/{device.deviceID}/inbox"
    )
    request_json = {
        'topic': auto_sub_topic,
        'qos': 1,
        'device_id': device_id
    }
    emqx_sub_url = f"{current_app.config['EMQX_API']}/mqtt/subscribe"
    with SyncHttp(auth=current_app.config['EMQX_AUTH']) as sync_http:
        sync_http.post(
            url=emqx_sub_url, json=request_json
        )


def message_acked_callback(request_dict) -> None:
    """ Update the publish status when the device receives the publish message """

    device_id = request_dict.get('client_id')
    payload = request_dict.get('payload')
    if not device_id or not payload:
        raise DataNotFound()
    try:
        load_payload = json.loads(payload)
    except Exception:
        raise DataNotFound()
    task_id = load_payload.get('task_id')
    if not task_id:
        raise DataNotFound()
    publish_log = PublishLog.query.filter(PublishLog.taskID == task_id).first_or_404()
    publish_log.publishStatus = 2
    publish_log.update()
