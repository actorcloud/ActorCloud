from collections import defaultdict

import arrow
from flask import jsonify, request
from sqlalchemy import func, column

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from actor_libs.types.orm import BaseQueryT
from app import auth
from app.models import Device, DeviceEvent, StreamPoint, DataStream, DataPoint
from . import bp


@bp.route('/devices/<int:device_id>/charts')
@auth.login_required
def list_device_charts(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID, Device.productID) \
        .filter(DeviceEvent.id == device_id).first_or_404()

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


def _filter_request_args(query: BaseQueryT) -> BaseQueryT:
    """ filter timeUnit args """

    time_unit = request.args('timeUnit')
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
    query = query.filter(DeviceEvent.msgTime > str_start_time)
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
        .filter(DataStream.productID == product_uid) \
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
    stream_point_info = _query_stream_points(product_uid)
    records = []
    stream_points_events = defaultdict(list)
    # collecting device_event under stream_points
    for device_event in device_events:
        _key = f"{device_event.streamID}:{device_event.dataPointID}"
        stream_points_events[_key].append(dict(device_event))
    # build record
    for _key, events_info in stream_points_events.items():
        stream_uid, data_point_uid = _key.splite(':')
        stream_point = stream_point_info[_key]
        record = {
            'streamID': stream_uid,
            'dataPointID': data_point_uid,
            'chartName': (
                f"{stream_point['streamName']}",
                f"/{stream_point['datePointName']}"
            )
        }
        chart_time = []
        chart_value = []
        for event_info in events_info:
            chart_time.append(event_info['msgTime'])
            chart_value.append(event_info['value'])
        record['chartData'] = {'time': chart_time, 'value': chart_value}
        records.append(record)
    return records
