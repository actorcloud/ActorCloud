from datetime import datetime

from flask import jsonify, request, current_app
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound, AuthFailed
from actor_libs.http_tools import SyncHttp
from app.models import Product, Client, DictCode, CertAuth, Cert, ConnectLog
from . import bp


@bp.route('/emqx/auth', methods=['POST'])
def client_auth():
    request_form = request.form
    device_uid = request_form.get('device_id')
    cn = request_form.get('cn')
    connect_date = datetime.now()
    # query client info
    query = db.session \
        .query(Client, func.lower(DictCode.enLabel).label('protocol')) \
        .join(Product, Product.productID == Client.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Client.deviceID == device_uid, Client.blocked == 0,
                DictCode.code == 'cloudProtocol')
    if cn is None or cn == 'undefined':
        # token auth
        query = query.filter(Client.authType == 1)
    else:
        # cert auth
        query = query \
            .join(CertAuth, CertAuth.deviceIntID == Client.id) \
            .join(Cert, Cert.CN == CertAuth.CN) \
            .filter(CertAuth.CN == cn, Cert.enable == 1, Client.authType == 2)
    client_info = query.first()
    if not client_info:
        raise AuthFailed(field='device')
    client, protocol = client_info
    auth_status = validate_connect_auth(client, protocol, request_form)
    # insert connect_logs
    connect_dict = {
        'IP': request_form.get('ip'),
        'msgTime': connect_date,
        'deviceID': client.deviceID,
        'tenantID': client.tenantID
    }
    connect_log = ConnectLog()
    if auth_status:
        connect_dict['connectStatus'] = 1
        client.deviceStatus = 1
        client.lastConnection = connect_date
        record = {
            'mountpoint': f'/{protocol}/{client.tenantID}/{client.productID}/{client.deviceID}/'
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
    }
    if not handle_action_funcs.get(callback_action):
        raise DataNotFound()
    handle_action = handle_action_funcs[callback_action]
    handle_action(request_dict)
    return '', 201


def validate_connect_auth(client, protocol, request_form) -> bool:
    if protocol == 'lwm2m' or client.authType == 2:
        auth_status = True
    elif all([client.authType == 1,
              client.deviceUsername == request_form.get('username'),
              client.token == request_form.get('password')]):
        auth_status = True
    else:
        auth_status = False
    return auth_status


def client_disconnected_callback(request_dict) -> None:
    client_id = request_dict.get('client_id')
    if not client_id:
        return
    client = Client.query.filter(Client.deviceID == client_id).first()
    if not client:
        return
    connect_dict = {
        'msgTime': request_dict['callback_date'],
        'deviceID': client.deviceID,
        'tenantID': client.tenantID,
        'connectStatus': 0
    }
    connect_log = ConnectLog()
    connect_log.create(request_dict=connect_dict, commit=False)
    client.deviceStatus = 0
    client.update()


def client_connected_callback(request_dict) -> None:
    """ client connected subscribe inbox topic """

    client_id = request_dict.get('client_id')
    if not client_id:
        return
    client = db.session \
        .query(Client.tenantID, Client.productID,
               Client.deviceID, func.lower(DictCode.enLabel).label('protocol')) \
        .join(Product, Product.productID == Client.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Client.deviceID == client_id, DictCode.code == 'cloudProtocol') \
        .first()
    if not client or client.protocol == 'lwm2m':
        # if client protocol is lwm2m pass
        return

    auto_sub_topic = (
        f"/{client.protocol}/{client.tenantID}"
        f"/{client.productID}/{client.deviceID}/inbox"
    )
    request_json = {
        'topic': auto_sub_topic,
        'qos': 1,
        'client_id': client_id
    }
    emqx_sub_url = f"{current_app.config['EMQX_API']}/mqtt/subscribe"
    with SyncHttp(auth=current_app.config['EMQX_AUTH']) as sync_http:
        sync_http.post(
            url=emqx_sub_url, json=request_json
        )
