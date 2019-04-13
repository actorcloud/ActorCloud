from flask import jsonify, request, g
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.database.sql.base import fetch_many
from actor_libs.errors import ReferencedError, ResourceLimited
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    Channel, User, Gateway, Device, Product, Tag, ClientTag
)
from app.schemas import GatewaySchema, GatewayUpdateSchema, ChannelSchema
from . import bp


@bp.route('/gateways')
@auth.login_required
def list_gateways():
    code_list = [
        'authType', 'deviceStatus', 'cloudProtocol', 'gatewayProtocol',
        'upLinkNetwork'
    ]
    query = Gateway.query \
        .join(Product, Product.productID == Gateway.productID) \
        .with_entities(Gateway, Product.productName,
                       Product.cloudProtocol, Product.gatewayProtocol)

    product_uid = request.args.get('productID')
    if product_uid and isinstance(product_uid, str):
        query = query.filter(Product.productID == product_uid)

    query = tag_query(query)

    records = query.pagination(code_list=code_list)
    gateway_ids = [record['id'] for record in records['items']]
    query = db.session \
        .query(Device.gateway, func.count(Device.id)) \
        .group_by(Device.gateway) \
        .filter(Device.gateway.in_(gateway_ids)).all()
    device_count_dict = dict(query)
    for record in records['items']:
        record['deviceCount'] = device_count_dict.get(record['id'], 0)
    return jsonify(records)


@bp.route('/gateways/<int:gateway_id>')
@auth.login_required
def view_gateway(gateway_id):
    query = Gateway.query \
        .join(Product, Product.productID == Gateway.productID) \
        .filter(Gateway.id == gateway_id) \
        .with_entities(Gateway, User.username, Product.productName,
                       Product.cloudProtocol, Product.gatewayProtocol)

    code_list = ['cloudProtocol', 'gatewayProtocol', 'upLinkNetwork']
    record = query.to_dict(code_list=code_list)

    tags = []
    tags_index = []
    query_tags = Tag.query \
        .join(ClientTag) \
        .filter(ClientTag.c.deviceIntID == gateway_id) \
        .all()
    for tag in query_tags:
        tags.append(tag.tagID)
        tags_index.append({'value': tag.id, 'label': tag.tagName})
    record['tags'] = tags
    record['tagIndex'] = tags_index
    return jsonify(record)


@bp.route('/gateways', methods=['POST'])
@auth.login_required
def create_gateway():
    request_dict = GatewaySchema.validate_request()
    request_dict['userIntID'] = g.user_id
    request_dict['tenantID'] = g.tenant_uid

    gateway = Gateway()
    new_gateway = gateway.create(request_dict)
    record = new_gateway.to_dict()
    record['gatewayProtocol'] = request_dict['gatewayProtocol']
    return jsonify(record), 201


@bp.route('/gateways/<int:gateway_id>', methods=['PUT'])
@auth.login_required
def update_gateway(gateway_id):
    gateway = Gateway.query.filter(Gateway.id == gateway_id).first_or_404()
    request_dict = GatewayUpdateSchema.validate_request(obj=gateway)
    updated_gateway = gateway.update(request_dict)
    record = updated_gateway.to_dict()
    record['gatewayProtocol'] = request_dict['gatewayProtocol']
    return jsonify(record)


@bp.route('/gateways', methods=['DELETE'])
@auth.login_required
def delete_gateway():
    delete_ids = get_delete_ids()
    query_results = Gateway.query \
        .filter(Gateway.id.in_(delete_ids)) \
        .many()
    try:
        for gateway in query_results:
            if gateway.devices:
                raise ReferencedError()
            db.session.delete(gateway)
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/gateways/<int:gateway_id>/channels')
@auth.login_required
def list_gateway_channel(gateway_id):
    query = Channel.query \
        .filter(Channel.gateway == gateway_id)
    records = query.pagination()
    items = records['items']
    records['channelType'] = items[0]['channelType'] if items else None
    return jsonify(records)


@bp.route('/gateways/<int:gateway_id>/channels/<int:channel_id>')
@auth.login_required
def view_gateway_channel(gateway_id, channel_id):
    query = Channel.query \
        .filter(Channel.gateway == gateway_id,
                Channel.id == channel_id)

    record = query.to_dict()
    return jsonify(record)


@bp.route('/gateways/<int:gateway_id>/channels', methods=['POST'])
def create_gateway_channel(gateway_id):
    request_dict = ChannelSchema.validate_request()
    request_dict['gateway'] = gateway_id
    channel_type = request_dict['channelType']
    all_channel_type = db.session.query(Channel.channelType) \
        .filter(Channel.gateway == gateway_id) \
        .all()
    com_channel_type = db.session.query(Channel.channelType) \
        .filter(Channel.gateway == gateway_id,
                Channel.channelType == 'COM') \
        .all()
    if channel_type == 'COM' and all_channel_type:
        raise ResourceLimited(field='COM')
    elif channel_type == 'TCP' and com_channel_type:
        raise ResourceLimited(field='COM')
    elif channel_type == 'TCP' and len(all_channel_type) >= 9:
        raise ResourceLimited(field='TCP')
    else:
        pass
    channel = Channel()
    new_channel = channel.create(request_dict)
    record = new_channel.to_dict()
    return jsonify(record), 201


@bp.route('/gateways/<int:gateway_id>/channels/<int:channel_id>', methods=['PUT'])
@auth.login_required
def update_gateway_channel(gateway_id, channel_id):
    channel = Channel.query \
        .filter(Channel.gateway == gateway_id,
                Channel.id == channel_id) \
        .first_or_404()
    request_dict = ChannelSchema.validate_request(obj=channel)
    request_dict['gateway'] = gateway_id
    updated_gateway = channel.update(request_dict)
    record = updated_gateway.to_dict()
    return jsonify(record)


@bp.route('/gateways/<int:gateway_id>/channels', methods=['DELETE'])
@auth.login_required
def delete_gateway_channel(gateway_id):
    gateway = Gateway.query.filter(Gateway.id == gateway_id).first_or_404()
    delete_ids = get_delete_ids()
    query_results = Channel.query \
        .filter(Channel.id.in_(delete_ids),
                Channel.gateway == gateway.id) \
        .many()
    try:
        for channel in query_results:
            db.session.delete(channel)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/gateways/<int:gateway_id>/devices_data')
@auth.login_required
def gateway_devices_data(gateway_id):
    Gateway.query.filter(Gateway.id == gateway_id).first_or_404()

    device_name = request.args.get('deviceName_like')
    devices_query = Device.query.filter(Device.gateway == gateway_id) \
        .with_entities(Device.deviceID, Device.deviceName)
    if device_name:
        devices_query = devices_query \
            .filter(Device.deviceName.ilike(f'%{device_name}%'))
    devices = [f"('{device.deviceID}', '{device.deviceName}')" for device in devices_query.all()]
    if devices:
        query_devices = ','.join(devices)

        query_sql = f"""
            WITH filter_devices("deviceID", "deviceName") AS (VALUES {query_devices})
            SELECT
                TO_CHAR(filter_events."msgTime", 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
                filter_devices."deviceName", json.name as "dataPointName", json.value
            FROM (
                SELECT DISTINCT ON ("tenantID", "deviceID") *
                FROM device_events
                WHERE device_events."msgTime" >= NOW() - INTERVAL '1 week'
                    AND device_events."tenantID" = '{g.tenant_uid}'
                ORDER BY "tenantID", "deviceID", "msgTime" desc
            ) filter_events
            JOIN
                filter_devices ON filter_devices."deviceID" = filter_events."deviceID"
            CROSS JOIN LATERAL
                JSONB_TO_RECORDSET(filter_events.payload_json) AS json(name text, value text)
        """
        records = fetch_many(query_sql)
    else:
        records = []
    return jsonify(records)


def tag_query(query):
    tag_uid = request.args.get('tagID', type=str)
    if tag_uid:
        gateway_query = db.session.query(ClientTag.c.deviceIntID) \
            .filter(ClientTag.c.tagID == tag_uid) \
            .all()
        filter_gateways = [gateway[0] for gateway in gateway_query]
        query = query.filter(Gateway.id.in_(filter_gateways))
    tag_name = request.args.get('tagName_like', type=str)
    if tag_name:
        gateway_query = db.session.query(ClientTag.c.deviceIntID) \
            .join(Tag, Tag.tagID == ClientTag.c.tagID) \
            .filter(Tag.tagName.ilike(f'%{tag_name}%')) \
            .all()
        filter_gateways = [gateway[0] for gateway in gateway_query]
        query = query.filter(Gateway.id.in_(filter_gateways))
    return query
