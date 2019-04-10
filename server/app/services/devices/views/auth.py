from flask import jsonify, request
from sqlalchemy import func

from actor_libs.database.orm import db
from app.models import Product, Client, DictCode

from . import bp


@bp.route('/client/auth', methods=['POST'])
def client_auth():
    params = request.form
    client_id = params.get('clientid')
    username = params.get('username')
    password = params.get('password')
    query_result = db.session.query(Client, func.lower(DictCode.enLabel)) \
        .join(Product, Product.productID == Client.productID) \
        .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
        .filter(Client.deviceID == client_id, Client.deviceUsername == username,
                Client.token == password, Client.blocked == 0, DictCode.code == 'cloudProtocol') \
        .first()
    if not query_result:
        return '', 401
    client, protocol = query_result
    result = {
        'mountpoint': f'/{protocol}/{client.tenantID}/{client.productID}/{client.deviceID}'
    }
    return jsonify(result)
