from datetime import datetime

from flask import jsonify, request
from sqlalchemy import func

from actor_libs.database.orm import db
from app.models import Product, Client, DictCode, CertAuth, Cert

from . import bp


@bp.route('/client/auth', methods=['POST'])
def client_auth():
    params = request.form
    client_id = params.get('clientid')
    username = params.get('username')
    password = params.get('password')
    cn = params.get('cn')

    query = db.session \
        .query(Client, func.lower(DictCode.enLabel)) \
        .join(Product, Product.productID == Client.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Client.deviceID == client_id, Client.blocked == 0, DictCode.code == 'cloudProtocol')

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

    if not query_result:
        return '', 401

    client, protocol = query_result
    client.lastConnection = datetime.now()
    client.update()
    result = {
        'mountpoint': f'/{protocol}/{client.tenantID}/{client.productID}/{client.deviceID}'
    }
    return jsonify(result)
