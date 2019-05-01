import arrow
from flask import request, jsonify
from sqlalchemy import func, column

from actor_libs.database.orm import db
from app import auth
from app.models import Client, Product, DeviceEvent, DataStream, DataPoint, StreamPoint
from . import bp
from ._utils import add_time_filter


@bp.route('/devices/<int:client_id>/capability_data')
@bp.route('/gateways/<int:client_id>/capability_data')
@auth.login_required
def list_capability_data(client_id):
    client = Client.query \
        .join(Product, Product.productID == Client.productID) \
        .with_entities(Client.deviceID, Client.productID, Product.cloudProtocol) \
        .filter(Client.id == client_id) \
        .first_or_404()

    events_query = db.session \
        .query(DeviceEvent.msgTime, DeviceEvent.streamID,
               column('key').label('dataPointID'), column('value')) \
        .select_from(DeviceEvent, func.jsonb_each(DeviceEvent.data)) \
        .filter(DeviceEvent.deviceID == client.deviceID) \
        .filter(DeviceEvent.dataType == 1)

    # filter data point
    data_point_id = request.args.get('dataPointID')
    if data_point_id:
        events_query = events_query.filter(column('key') == data_point_id)

    events_query = add_time_filter(events_query)
    events = events_query.pagination()

    data_points = _get_data_points(client.productID)
    records = _get_capability_data(events, data_points)

    return jsonify(records)


def _get_capability_data(events, data_points):
    items = events.get('items')
    items_with_name = []
    for item in items:
        # get data point name and data stream name
        data_point_key = f'{item.get("streamID")}:{item.get("dataPointID")}'
        name_dict = data_points.get(data_point_key)
        item['streamName'] = name_dict.get('stream_name')
        item['dataPointName'] = name_dict.get('data_point_name')

        # get data point value and msgTime
        value = item.get('value')
        if isinstance(value, dict):
            ts = value.get('time')
            item['msgTime'] = arrow.get(ts).format('YYYY-MM-DD HH:mm:ss')
            item['value'] = value.get('value')
        items_with_name.append(item)
    events['items'] = items_with_name
    return events


def _get_data_points(product_id):
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
        .filter(DataStream.productID == product_id) \
        .many()

    data_points_dict = {}
    for stream_id, stream_name, data_point_id, data_point_name in data_points:
        key = f'{stream_id}:{data_point_id}'
        data_points_dict[key] = {
            'data_point_name': data_point_name,
            'stream_name': stream_name
        }

    return data_points_dict
