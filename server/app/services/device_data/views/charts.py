from collections import defaultdict
from operator import itemgetter

import arrow
from flask import jsonify, request
from sqlalchemy import func, column, desc

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from actor_libs.types.orm import BaseQueryT
from actor_libs.utils import format_timestamp
from app import auth
from app.models import (
    Device, DeviceEvent, StreamPoint,
    DataStream, DataPoint, DeviceEventLatest
)
from . import bp


@bp.route('/devices/<int:device_id>/charts')
@auth.login_required
def list_device_charts(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID, Device.productID) \
        .filter(Device.id == device_id).first_or_404()

    query = db.session \
        .query(DeviceEvent.msgTime, DeviceEvent.streamID,
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEvent, func.jsonb_each(DeviceEvent.data)) \
        .filter(DeviceEvent.dataType == 1,
                DeviceEvent.tenantID == device.tenantID,
                DeviceEvent.deviceID == device.deviceID)
    device_events = _filter_request_args(query).all()
    records = _handle_device_events(device_events, device.productID)
    return jsonify(records)


@bp.route('/devices/<int:device_id>/last_data_charts')
@auth.login_required
def list_last_data_charts(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID, Device.productID) \
        .filter(Device.id == device_id).first_or_404()

    latest_device_events = db.session \
        .query(DeviceEventLatest.msgTime, DeviceEventLatest.streamID,
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEventLatest, func.jsonb_each(DeviceEventLatest.data)) \
        .filter(DeviceEventLatest.dataType == 1,
                DeviceEventLatest.tenantID == device.tenantID,
                DeviceEventLatest.deviceID == device.deviceID).all()
    records = []
    stream_point_info = _query_stream_points(device.productID)
    for _key, _info in stream_point_info.items():
        record = {
            'streamID': _key.split(':')[0],
            'dataPointID': _key.split(':')[1],
            'chartName': f"{_info['streamName']}/{_info['dataPointName']}",
            'chartData': None
        }
        for device_event in latest_device_events:
            event_dict = device_event_to_dict(device_event)
            event_key = f"{event_dict['streamID']}:{event_dict['dataPointID']}"
            if _key == event_key:
                record['chartData'] = {
                    'time': event_dict['msgTime'],
                    'value': event_dict['value']
                }
            else:
                continue
        records.append(record)
    return jsonify(records)


def _filter_request_args(query: BaseQueryT) -> BaseQueryT:
    """ filter timeUnit args """

    time_unit = request.args.get('timeUnit', type=str)
    date_now = arrow.now()
    time_unit_dict = {
        '5m': date_now.shift(minutes=-5),
        '1h': date_now.shift(hours=-1),
        '6h': date_now.shift(hours=-6),
        '1d': date_now.shift(days=-1),
        '1w': date_now.shift(weeks=-1)
    }
    start_time = time_unit_dict.get(time_unit)
    if not start_time:
        raise ParameterInvalid(field='timeUnit')
    str_start_time = start_time.format()
    query = query \
        .filter(DeviceEvent.msgTime > str_start_time) \
        .order_by(desc(DeviceEvent.msgTime)) \
        .limit(2048)
    return query


def _query_stream_points(product_uid):
    """
    stream_point info format:
        {"streamID:dataPointID": {"streamName": xx, "dataPointName": xx}}
    """
    stream_points = db.session \
        .query(DataStream.streamID, DataStream.streamName,
               DataPoint.dataPointID, DataPoint.dataPointName) \
        .join(StreamPoint, DataStream.id == StreamPoint.c.dataStreamIntID) \
        .join(DataPoint, DataPoint.id == StreamPoint.c.dataPointIntID) \
        .filter(DataStream.productID == product_uid,
                DataPoint.pointDataType == 1) \
        .all()

    stream_point_info = defaultdict(dict)
    for stream_point in stream_points:
        _key = f"{stream_point.streamID}:{stream_point.dataPointID}"
        _value = {
            'streamName': stream_point.streamName,
            'dataPointName': stream_point.dataPointName
        }
        stream_point_info[_key] = _value
    return stream_point_info


def _handle_device_events(device_events, product_uid):
    """
    records format:
        [
          {
            "dataPointID": "temp",
            "streamID": "temp_hum",
            "chartName": "streamName/dataPointName",
            "chartData": {time: 353453453, value: 23}
          }
        ]
    """
    records = []
    stream_points_events = defaultdict(list)
    # collecting device_event under stream_points
    _to_dict = device_event_to_dict  # convert dict
    for device_event in device_events:
        _key = f"{device_event.streamID}:{device_event.dataPointID}"
        stream_points_events[_key].append(_to_dict(device_event))
    # build record
    stream_point_info = _query_stream_points(product_uid)
    for _key, _info in stream_point_info.items():
        record = {
            'streamID': _key.split(':')[0],
            'dataPointID': _key.split(':')[1],
            'chartName': f"{_info['streamName']}/{_info['dataPointName']}",
            'chartData': {'time': [], 'value': []}
        }
        events_info = stream_points_events.get(_key)
        if not events_info:
            records.append(record)
            continue
        chart_time = []
        chart_value = []
        events_info = sorted(events_info, key=itemgetter('msgTime'))
        for event_info in events_info:
            chart_time.append(event_info['msgTime'])
            chart_value.append(event_info['value'])
        record['chartData'] = {'time': chart_time, 'value': chart_value}
        records.append(record)
    return records


def device_event_to_dict(device_event):
    event_dict = {
        'msgTime': device_event.msgTime,
        'dataPointID': device_event.dataPointID,
        'streamID': device_event.streamID,
    }
    value = device_event.value
    if isinstance(value, dict):
        if value.get('time'):
            ts = value.get('time')
            event_dict['msgTime'] = format_timestamp(ts)
        event_dict['value'] = value.get('value')
    else:
        event_dict['value'] = value
    return event_dict
