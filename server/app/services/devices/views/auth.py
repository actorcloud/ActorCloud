from datetime import datetime

from flask import jsonify, request
from sqlalchemy import func

from actor_libs.database.orm import db
from app.models import Product, Client, DictCode, CertAuth, Cert, ClientConnectLog
from . import bp


@bp.route('/client/auth', methods=['POST'])
def client_auth():
    params = request.form
    device_uid = params.get('clientid')
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
        'keepAlive': params.get('keepAlive'), 'Ip': params.get('IP'),
        'msgTime': connect_date, 'deviceID': device_uid
    }
    connect_log = ClientConnectLog()
    if not query_result:
        # auth failed
        tenant_uid = db.session.query(Client.tenantID) \
            .filter(Client.deviceID == device_uid).first()
        if tenant_uid:
            connect_dict['tenantID'] = tenant_uid
            connect_dict['connectStatus'] = 2  # authenticate failed
            connect_log.create(request_dict=connect_dict, commit=False)
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
