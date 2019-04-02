import re
import ujson
from collections import defaultdict
from typing import Dict

from flask import jsonify, request, g, current_app
from sqlalchemy import func, text, desc
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.database.sql.base import fetch_many
from actor_libs.decorators import ip_limit
from actor_libs.errors import (
    ReferencedError, FormInvalid, ResourceLimited,
    AttributeUndefined, APIException, ParameterInvalid
)
from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.tasks.task import get_task_result
from actor_libs.utils import generate_uuid, validate_time_period_query, get_delete_ids
from app import auth
from app.models import (
    Channel, User, DictCode, Gateway, Device, DeviceEvent,
    Product, DataPoint, DeviceControlLog, Tag, ClientTag
)
from . import bp
from ..schemas import GatewaySchema, GatewayUpdateSchema, ChannelSchema


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


@bp.route('/gateways/<int:gateway_id>/events')
@auth.login_required
def view_gateway_events(gateway_id):
    gateway = Gateway.query \
        .with_entities(Gateway.deviceID, Gateway.tenantID) \
        .filter(Gateway.id == gateway_id) \
        .first_or_404()

    events_query = DeviceEvent.query \
        .filter(DeviceEvent.deviceID == gateway.deviceID,
                DeviceEvent.tenantID == gateway.tenantID) \
        .with_entities(DeviceEvent, Gateway.deviceName.label('gatewayName'))

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

    events_query = events_query.order_by(desc(DeviceEvent.msgTime))
    records = events_query.pagination()

    return jsonify(records)


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


@bp.route('/gateway_publish', methods=['POST'])
@auth.login_required
def gateway_publish():
    request_json = request.get_json()
    gateway_id = request_json.get('gateway')
    if not gateway_id:
        raise FormInvalid(field='gateway')
    gateway, payload = get_gateway_payload(gateway_id)
    record = emqx_gateway_publish(gateway, payload, g.user_id)
    if record.get('status') != 3:
        raise APIException(field='gateway_publish')
    return jsonify(record), 201


@bp.route('/gateways/<int:gateway_id>/control_logs')
@auth.login_required
def gateway_control_logs(gateway_id):
    gateway = Gateway.query \
        .with_entities(Gateway.id) \
        .filter(Gateway.id == gateway_id) \
        .first_or_404()

    control_query = DeviceControlLog.query \
        .join(User, User.id == DeviceControlLog.userIntID) \
        .with_entities(DeviceControlLog, User.username.label('createUser')) \
        .filter(DeviceControlLog.deviceIntID == gateway.id)
    records = control_query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/gateway/publish_callback', methods=['POST'])
@ip_limit
def gateway_publish_callback():
    """
    网关回调接口：
    Gateway callback
    1.normal callback
    2.EMQX forward Neuron gateway response
    Neuron gateway：
    success: {'func':4, 'kbid':{task_id}}
    fail: {'errc':1, 'efun':4,'kbid':{task_id}}
    """

    request_data = request.get_data()
    try:
        request_dict = ujson.loads(re.sub(r'\x00$', '', request_data))
    except ValueError:
        raise APIException()
    # normal callback
    task_uid = request_dict.get('task_id')
    if task_uid:
        control_log = DeviceControlLog.query. \
            filter(DeviceControlLog.taskID == task_uid).first()
        control_log.publishStatus = 2
        db.session.commit()

    # Neuron gateway response
    kbid = request_dict.get('kbid')
    if kbid:
        query = DeviceControlLog.query \
            .join(Gateway, Gateway.id == DeviceControlLog.deviceIntID) \
            .with_entities(DeviceControlLog, Gateway) \
            .filter(DeviceControlLog.taskID == kbid) \
            .first()
        if query:
            control_log, gateway = query
            if 'errc' in request_dict:
                control_log.publishStatus = 5
            else:
                control_log.publishStatus = 4
                gateway_func = request_dict.get('func')
                if gateway_func == 4:
                    # Config success,then restart to apply config
                    payload = {
                        'func': 40,
                        'acts': 'restartnew',
                        'kbid': generate_uuid()
                    }
                    emqx_gateway_publish(gateway, payload, control_log.userIntID)
        db.session.commit()
    return '', 201


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


def emqx_gateway_publish(gateway: Gateway, payload: dict, user_id: int) -> Dict:
    """ Neuron gateway """

    topic = f'{gateway.deviceID}/Request'
    control_log = DeviceControlLog(
        deviceIntID=gateway.id,
        payload=payload,
        userIntID=user_id,
        taskID=payload.get('kbid'),
        topic=topic,
        publishStatus=1,
        controlType=1
    )
    db.session.add(control_log)
    db.session.flush()
    task_uid = control_log.taskID

    callback = current_app.config.get('GATEWAY_CALLBACK_URL')
    request_payload = {
        'topic': topic,
        'protocol': 'mqtt',
        'tenantID': gateway.tenantID,
        'productID': gateway.productID,
        'deviceID': gateway.deviceID,
        'qos': 1,
        'callback': callback,
        'payload': ujson.dumps(payload),
        'task_id': task_uid
    }
    request_url = current_app.config.get('MQTT_PUBLISH_URL')
    emq_auth = current_app.config.get('EMQ_AUTH')

    with SyncHttp(auth=emq_auth) as sync_http:
        response = sync_http.post(request_url, json=request_payload)
    handled_response = handle_emqx_publish_response(response)
    if handled_response.get('status') == 3:
        task_result = get_task_result(status=3, message='Gateway publish success')
    else:
        control_log.publishStatus = 0
        task_result = get_task_result(status=4, message=handled_response.get('error'))
    db.session.commit()
    return task_result


def get_gateway_payload(gateway_id):
    """
    Neuron gateway
    Temporarily only supports COM channels
    """
    gateway = Gateway.query \
        .filter(Gateway.id == gateway_id, Gateway.tenantID == g.tenant_uid) \
        .first_or_404()
    channels = gateway.channels
    # validate channel
    if len(channels) != 1:
        raise AttributeUndefined(field='channel')
    channel = channels[0]
    if channel.channelType != 'COM':
        raise AttributeUndefined(field='channel')
    device_int_ids = [result.id for result in gateway.devices]
    # validate child devices
    if not device_int_ids:
        raise AttributeUndefined(field='groupDevice')
    query_results = Device.query \
        .outerjoin(DataPoint, DataPoint.productID == Device.productID) \
        .filter(Device.id.in_(device_int_ids)) \
        .with_entities(Device.id.label('deviceIntID'),
                       DataPoint.id.label('dataPointIntID'),
                       Device.deviceID, Device.modBusIndex,
                       DataPoint.dataPointID, DataPoint.binarySize,
                       DataPoint.pointDataType, DataPoint.registerAddr,
                       DataPoint.dataTransType, DataPoint.decimal) \
        .all()

    dict_code_list = DictCode.query \
        .filter(DictCode.code == 'pointDataType') \
        .all()
    point_data_type = {
        dict_code.codeValue: dict_code.codeStringValue
        for dict_code in dict_code_list
        if dict_code.codeStringValue is not None
    }
    channel_list = []
    default_channel = {
        "chntype": "dmy",
        "chnix": 0,
        "chnno": 0,
        "chnname": "Dummy",
        "chndrv": "-",
        "tcphost": "",
        "tcpport": 0,
        "ttycom": "",
        "ttybaud": 0,
        "ttydata": 0,
        "ttystop": "",
        "ttypari": "N",
        "ttycts": 0,
        "ttyrts": 0,
        "ttyorts": 0,
        "ttymodm": 0,
        "device": [{
            "tagname": "DUMMY",
            "tagtype": "L",
            "tagarrsz": 100,
            "tagaddr": "-",
            "tagattr": "-",
            "tagupdtime": 0,
            "taglogtime": 0,
            "tagsubno": 0,
            "tagstatus": "NNN"
        }]
    }
    channel_list.append(default_channel)
    channel_dict = {
        # COM channel，fixed value
        "chntype": "tty",
        "chnix": 1,
        "chnno": 1,
        # COM channel，fixed value
        "chnname": "Modbus RTU",
        "chndrv": "simdrv",
        "tcphost": "",
        "tcpport": 0,
        "ttycom": channel.COM,
        "ttybaud": channel.Baud,
        "ttydata": channel.Data,
        "ttystop": channel.Stop,
        "ttypari": channel.Parity,
        "ttycts": 0,
        "ttyrts": 0,
        "ttyorts": 0,
        "ttymodm": 0,
        "device": []
    }
    devices = []
    # data_points
    device_data_point_dict = defaultdict(list)
    for result in query_results:
        if result.dataPointIntID is None:
            raise AttributeUndefined(field='data_point')
        tag_attr = 'R0' if result.dataTransType == 1 else 'W'
        device_dict = {
            "tagaddr": f"{result.modBusIndex}!{result.registerAddr}",
            "tagtype": "L",
            "tagarrsz": result.binarySize,
            "tagname": f"A{result.deviceIntID}{result.dataPointIntID}",
            "tagattr": tag_attr,
            "tagupdtime": 0,
            "taglogtime": 0,
            "tagsubno": 0,
            "tagstatus": "NNN"
        }
        devices.append(device_dict)

        device_data_point_dict[result.deviceIntID].append(result)

    channel_dict['device'] = devices
    channel_list.append(channel_dict)

    object_list = []
    for key in device_data_point_dict.keys():
        device_uid = device_data_point_dict.get(key)[0].deviceID
        object_dict = {
            "objid": "*",
            "objname": device_uid,
            "objdesc": "",
            "objsize": 1,
            "objupdtime": 5,
            "objlogtime": 0,
            "objstatus": "NYYN",
            "objattr": []
        }
        for data_point in device_data_point_dict.get(key):
            attr_dict = {
                "objix": 0,
                "attid": "*",
                "attname": data_point.dataPointID,
                "objprefix": "*",
                "objsuffix": "*",
                "attdesc": "",
                "atttype": point_data_type.get(data_point.pointDataType),
                "decimal": data_point.decimal if data_point.decimal is not None else 0,
                "maxval": 0,
                "minval": 0,
                "preset": 0,
                "unit": "",
                "tagname": f"A{key}{data_point.dataPointID}",
                "tagix": 0,
                "notag": 1,
                "attsubno": 0,
                "attstatus": "NYYN"
            }
            object_dict['objattr'].append(attr_dict)
        object_list.append(object_dict)

    payload = {
        'func': 4,
        'kbid': generate_uuid(),
        'channel': channel_list,
        'object': object_list,
        'message': []
    }
    return gateway, payload


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
