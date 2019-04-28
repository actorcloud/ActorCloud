from datetime import datetime

from flask import jsonify, request, current_app
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound
from actor_libs.http_tools import SyncHttp
from app.models import Product, Client, DictCode, CertAuth, Cert, ConnectLog
from . import bp


@bp.route('/emqx/auth', methods=['POST'])
def client_auth():
    params = request.form
    device_uid = params.get('device_id')
    username = params.get('username')
    password = params.get('password')
    cn = params.get('cn')
    connect_date = datetime.now()

    query = db.session \
        .query(Client, func.lower(DictCode.enLabel)) \
        .join(Product, Product.productID == Client.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Client.deviceID == device_uid, Client.blocked == 0,
                DictCode.code == 'cloudProtocol')

    if cn is None or cn == 'undefined':
        # token
        query_result = query \
            .filter(Client.deviceUsername == username, Client.token == password,
                    Client.authType == 1) \
            .first()
    else:
        # cert
        query_result = query \
            .join(CertAuth, CertAuth.deviceIntID == Client.id) \
            .join(Cert, Cert.CN == CertAuth.CN) \
            .filter(CertAuth.CN == cn, Cert.enable == 1, Client.authType == 2) \
            .first()
    connect_dict = {
        'keepAlive': params.get('keepAlive'), 'IP': params.get('ip'),
        'msgTime': connect_date, 'deviceID': device_uid
    }
    connect_log = ConnectLog()
    if not query_result:
        # auth failed
        tenant = db.session.query(Client.tenantID) \
            .filter(Client.deviceID == device_uid).first()
        if tenant:
            connect_dict['tenantID'] = tenant.tenantID
            connect_dict['connectStatus'] = 2  # authenticate failed
            connect_log.create(request_dict=connect_dict)
        return '', 401
    # insert connect logs
    client, protocol = query_result
    connect_dict['tenantID'] = client.tenantID
    connect_dict['connectStatus'] = 1  # Online
    connect_log.create(request_dict=connect_dict, commit=False)
    # update client deviceStatus and lastConnection
    client.deviceStatus = 1
    client.lastConnection = connect_date
    client.update()
    result = {
        'mountpoint': f'/{protocol}/{client.tenantID}/{client.productID}/{client.deviceID}/'
    }
    return jsonify(result)


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


def client_connected_callback(request_dict, topic='inbox') -> None:
    """ client connected subscribe inbox topic """

    client_id = request_dict.get('client_id')
    if not client_id:
        return
    client = Client.query \
        .join(Product, Product.productID == Client.productID) \
        .with_entities(Client.deviceID, Product.cloudProtocol) \
        .filter(Client.deviceID == client_id).first()
    if not client or client.cloudProtocol == 3:
        # if client protocol is lwm2m pass
        return

    request_json = {
        'topic': topic,
        'qos': 1,
        'client_id': client_id
    }
    emqx_sub_url = f"{current_app.config['EMQX_API']}/mqtt/subscribe"
    with SyncHttp(auth=current_app.config['EMQX_AUTH']) as sync_http:
        sync_http.post(
            url=emqx_sub_url, json=request_json
        )
