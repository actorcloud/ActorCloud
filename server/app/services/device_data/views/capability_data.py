from flask import request, jsonify, current_app
from sqlalchemy import func, column

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from actor_libs.utils import format_timestamp
from app import auth
from app.models import (
    Device, Product, DeviceEvent, DataStream, DataPoint, StreamPoint, Group, GroupDevice,
    DeviceEventLatest, EndDevice
)
from . import bp
from ._utils import validate_time_range


@bp.route('/devices/<int:device_id>/capability_data')
@auth.login_required
def list_device_capability_data(device_id):
    validate_time_range()
    device = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device.deviceID, Device.productID, Product.cloudProtocol) \
        .filter(Device.id == device_id) \
        .first_or_404()

    events_query = db.session \
        .query(DeviceEvent.msgTime, DeviceEvent.streamID,
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEvent, func.jsonb_each(DeviceEvent.data)) \
        .filter(DeviceEvent.deviceID == device.deviceID) \
        .filter(DeviceEvent.dataType == 1)

    # filter data point
    data_point_id = request.args.get('dataPointID')
    if data_point_id:
        events_query = events_query.filter(column('key') == data_point_id)

    events = events_query.pagination()

    data_points = _get_data_points([device.productID])
    events['items'] = _get_capability_data(events['items'], data_points)

    return jsonify(events)


@bp.route('/device_capability_data')
@auth.login_required
def list_devices_capability_data():
    """
    List the latest capability data of each device under group or gateway
    """
    group_id = request.args.get("groupIntID")
    gateway_id = request.args.get("gatewayIntID")

    if group_id:
        group = Group.query.with_entities(Group.groupID) \
            .filter(Group.id == group_id).first_or_404()
        devices_query = Device.query.with_entities(Device.deviceID, Device.productID) \
            .join(GroupDevice, GroupDevice.c.deviceIntID == Device.id) \
            .filter(GroupDevice.c.groupID == group.groupID)
    elif gateway_id:
        devices_query = Device.query.with_entities(Device.deviceID, Device.productID) \
            .join(EndDevice, EndDevice.id == Device.id) \
            .filter(EndDevice.gateway == gateway_id)
    else:
        raise ParameterInvalid()
    # search by device name
    device_name = request.args.get('deviceName_like')
    if device_name:
        devices_query = devices_query.filter(Device.deviceName.ilike(f'%{device_name}%'))
    devices = devices_query.all()
    devices_uid = [device.deviceID for device in devices]
    devices_product_uid = [device.productID for device in devices]

    events_query = db.session \
        .query(DeviceEventLatest.msgTime, DeviceEventLatest.streamID, DeviceEventLatest.deviceID,
               Device.deviceName, Device.id.label('deviceIntID'),
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEventLatest, func.jsonb_each(DeviceEventLatest.data)) \
        .join(Device, Device.deviceID == DeviceEventLatest.deviceID) \
        .filter(DeviceEventLatest.deviceID.in_(devices_uid)) \
        .filter(DeviceEventLatest.dataType == 1)

    # filter by data point
    data_point_id = request.args.get('dataPointID')
    if data_point_id:
        events_query = events_query.filter(column('key') == data_point_id)

    events = events_query.pagination()
    data_points = _get_data_points(devices_product_uid)
    events['items'] = _get_capability_data(events['items'], data_points)

    return jsonify(events)


@bp.route('/devices/<int:device_id>/last_capability_data')
@auth.login_required
def list_device_last_capability_data(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.productID) \
        .filter(Device.id == device_id) \
        .first_or_404()

    events_query = db.session \
        .query(DeviceEventLatest.msgTime, DeviceEventLatest.streamID,
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEventLatest, func.jsonb_each(DeviceEventLatest.data)) \
        .filter(DeviceEventLatest.deviceID == device.deviceID) \
        .filter(DeviceEventLatest.dataType == 1)

    # filter data point
    data_point_id = request.args.get('dataPointID')
    if data_point_id:
        events_query = events_query.filter(column('key') == data_point_id)

    events_result = events_query.all()
    events = []
    for event in events_result:
        event_dict = {}
        for key in event.keys():
            event_dict[key] = getattr(event, key)
        events.append(event_dict)

    data_points = _get_data_points([device.productID])

    records = _get_capability_data(events, data_points)

    return jsonify(records)


def _get_capability_data(events, data_points):
    items_with_name = []
    for item in events:
        # get data point name and data stream name
        data_point_key = f'{item.get("streamID")}:{item.get("dataPointID")}'
        name_dict = data_points.get(data_point_key)
        if not name_dict:
            continue
        item['streamName'] = name_dict.get('stream_name')
        item['dataPointName'] = name_dict.get('data_point_name')

        # get data point value and msgTime
        value = item.get('value')
        if isinstance(value, dict):
            ts = value.get('time')
            if len(str(ts)) == 10:
                item['msgTime'] = format_timestamp(ts, current_app.config['TIMEZONE'])
            item['value'] = value.get('value')
        items_with_name.append(item)
    return items_with_name


def _get_data_points(products_uid):
    """
    :return: {
        'stream_id:data_point_id': {'data_point_name': 'xxx', 'stream_name': 'yyy'}
    }
    """
    data_points = DataPoint.query \
        .join(StreamPoint, StreamPoint.c.dataPointIntID == DataPoint.id) \
        .join(DataStream, DataStream.id == StreamPoint.c.dataStreamIntID) \
        .with_entities(DataStream.streamID, DataStream.streamName,
                       DataPoint.dataPointID, DataPoint.dataPointName) \
        .filter(DataStream.productID.in_(products_uid)) \
        .many()

    data_points_dict = {}
    for stream_id, stream_name, data_point_id, data_point_name in data_points:
        key = f'{stream_id}:{data_point_id}'
        data_points_dict[key] = {
            'data_point_name': data_point_name,
            'stream_name': stream_name
        }

    return data_points_dict
