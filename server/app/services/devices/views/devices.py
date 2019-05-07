from typing import Tuple

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid, ReferencedError
from actor_libs.types.orm import BaseQueryT, BaseModelT
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Device, Product, EndDevice, Gateway, User
from app.schemas import EndDeviceSchema, GatewaySchema
from . import bp


@bp.route('/devices')
@auth.login_required
def list_devices():
    query = Device.query.join(Product, Product.productID == Device.productID)
    query = device_request_args_filter(query)
    code_list = ['authType', 'deviceStatus', 'cloudProtocol']
    records = query.pagination(code_list=code_list)
    return jsonify(records)


@bp.route('/devices/<int:device_id>')
@auth.login_required
def view_devices(device_id):
    query, model = device_query_object()
    code_list = ['authType', 'deviceStatus', 'cloudProtocol', 'gatewayProtocol']
    record = query.join(User, User.id == Device.userIntID) \
        .join(Product, Product.productID == Device.productID) \
        .filter(model.id == device_id) \
        .with_entities(model,
                       User.username.label('createUser'),
                       Product.id.label('productIntID'),
                       Product.productName,
                       Product.cloudProtocol,
                       Product.gatewayProtocol) \
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
        request_dict = GatewaySchema.validate_request()
    updated_device = device.update(request_dict)
    record = updated_device.to_dict()
    return jsonify(record), 201


@bp.route('/devices', methods=['DELETE'])
@auth.login_required
def delete_device():
    delete_ids = get_delete_ids()
    query, model = device_query_object()
    if model == EndDevice:
        # check endDevice under the delete endDevice
        parent_device = db.session.query(db.func.count(EndDevice.id)) \
            .filter(EndDevice.parentDevice.in_(delete_ids)) \
            .scalar()
        if parent_device != 0:
            raise ReferencedError(field='parentDevice')
    if model == Gateway:
        # check endDevice under the delete gateway
        gateway_device = db.session.query(db.func.count(EndDevice.id)) \
            .filter(EndDevice.gateway.in_(delete_ids)) \
            .scalar()
        if gateway_device != 0:
            raise ReferencedError(field='endDevice')
    query_results = query.filter(model.id.in_(delete_ids)).many()
    try:
        for device in query_results:
            db.session.delete(device)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def device_query_object() -> Tuple[BaseQueryT, BaseModelT]:
    device_type = request.args.get('deviceType', type=int)
    if device_type == 1:
        query, model = EndDevice.query, EndDevice
    elif device_type == 2:
        query, model = Gateway.query, Gateway
    else:
        raise ParameterInvalid(field='deviceType')
    return query, model


def device_request_args_filter(query: BaseQueryT) -> BaseQueryT:
    request_args = request.args
    if isinstance(request_args.get('productName'), str):
        query = query.filter(Product.productName.ilike(f"{request_args['productName']}"))
    elif isinstance(request_args.get('cloudProtocol'), int):
        query = query.filter(Product.cloudProtocol == request_args['cloudProtocol'])
    elif isinstance(request_args.get('gatewayProtocol'), int):
        query = query.filter(Product.gatewayProtocol == request_args['gatewayProtocol'])
    return query
