# modbus protocol gateway channel

from flask import jsonify

from sqlalchemy.exc import IntegrityError
from actor_libs.errors import ReferencedError, DataNotFound
from actor_libs.database.orm import db
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Device, Product, Channel
from app.schemas import ChannelSchema
from . import bp


@bp.route('/devices/<int:device_id>/channels')
@auth.login_required
def list_gateway_channel(device_id):
    device = _validate_channel_device(device_id)
    query = Channel.query.filter(Channel.gateway == device.id)
    records = query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/channels', methods=['POST'])
@auth.login_required
def create_gateway_channel(device_id):
    device = _validate_channel_device(device_id)
    request_dict = ChannelSchema.validate_request(obj=device)
    channel = Channel()
    new_channel = channel.create(request_dict)
    record = new_channel.to_dict()
    return jsonify(record), 201


@bp.route('/devices/<int:device_id>/channels', methods=['DELETE'])
@auth.login_required
def delete_gateway_channel(device_id):
    device = _validate_channel_device(device_id)
    delete_ids = get_delete_ids()
    channels = Channel.query\
        .filter(Channel.gateway == device.id, Channel.id.in_(set(delete_ids))) \
        .many(allow_none=False, expect_result=len(delete_ids))

    try:
        for channel in channels:
            db.session.delete(channel)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def _validate_channel_device(device_id):
    """ Validate device_id and gateway protocol """

    device = Device.query \
        .join(Product, Product.productID == Device.productID)\
        .filter(Device.id == device_id) \
        .with_entities(Device.id, Device.deviceType,
                       Product.gatewayProtocol).first_or_404()
    if device.deviceType != 2 or device.gatewayProtocol != 7:
        # if not gateway or gateway protocol is not modbus
        raise DataNotFound(field='URL')
    return device
