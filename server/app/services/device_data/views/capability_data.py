from flask import request, jsonify, g

from actor_libs.database.sql.base import fetch_many
from actor_libs.errors import ParameterInvalid
from actor_libs.utils import validate_time_period_query
from app import auth
from app.models import Device, Product
from . import bp


@bp.route('/capability_data')
@auth.login_required
def list_capability_data():
    device_uid = request.args.get('deviceID')
    if not isinstance(device_uid, str):
        raise ParameterInvalid(field='deviceID')

    lwm2m_type = request.args.get('lwm2mType', 'data_point')
    if lwm2m_type not in ['data_point', 'path']:
        raise ParameterInvalid(field='lwm2mType')

    device = Device.query.join(Product, Product.productID == Device.productID) \
        .with_entities(Device.deviceID, Product.productID, Product.cloudProtocol) \
        .filter(Device.deviceID == device_uid).first_or_404()

    if device.cloudProtocol == 1:
        capability_data = _mqtt_capability_data(device.deviceID)
    elif device.cloudProtocol in [3, 4]:
        capability_data = _lwm2m_capability_data(device.deviceID)
        if lwm2m_type != 'data_point':
            capability_data = _lwm2m_data(device.deviceID)
    elif device.cloudProtocol == 7:
        capability_data = _modbus_capability_data(device.deviceID)
    else:
        capability_data = []
    return jsonify(capability_data)


def _mqtt_capability_data(device_uid: str):
    # to_char(to_timestamp(json.time), 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
    query_sql = f"""
        SELECT
            to_char(events."msgTime", 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
            data_streams."streamName", data_points."dataPointName", json.value
        FROM
            device_events events
        CROSS JOIN LATERAL
            jsonb_to_recordset(events.payload_json) as json(name text, value text)
        JOIN
            data_streams on data_streams."tenantID"=events."tenantID"
                and data_streams."productID"=events."productID"
                and data_streams.topic=events.topic
        JOIN
            data_points on data_points."tenantID"=events."tenantID"
                and data_points."productID"=events."productID"
                and data_points."dataPointID"=json.name
        WHERE
            events."tenantID"='{g.tenant_uid}' and events."deviceID"='{device_uid}'
    """
    data_stream_id = request.args.get('dataStreamIntID', type=int)
    if data_stream_id:
        query_sql = f"""
            {query_sql}
            and data_streams.id={data_stream_id}
        """
    data_point_id = request.args.get('dataPointID', type=str)
    if data_point_id:
        query_sql = f"""
            {query_sql}
            and data_points."dataPointID"='{data_point_id}'
        """
    query_sql = _handle_time_filter(query_sql)
    records = fetch_many(query_sql)
    return records


def _lwm2m_capability_data(device_uid: str):
    query_sql = f"""
        SELECT
            to_char(events."msgTime", 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
            data_streams."streamName", data_points."dataPointName", json.value
        FROM
            device_events events
        CROSS JOIN LATERAL
            jsonb_to_recordset(events.payload_json)
                as json(name text, value text, stream_id integer)
        JOIN
            data_streams on data_streams."tenantID"=events."tenantID"
                and data_streams."productID"=events."productID"
                and data_streams."streamID"=json.stream_id
        JOIN
            data_points on data_points."tenantID"=events."tenantID"
                and data_points."productID"=events."productID"
                and data_points."dataPointID"=json.name
        WHERE
            events."tenantID"='{g.tenant_uid}' and events."deviceID"='{device_uid}'
    """
    data_stream_id = request.args.get('dataStreamIntID', type=int)
    if data_stream_id:
        query_sql = f"""
            {query_sql}
            and data_streams.id={data_stream_id}
        """
    data_point_id = request.args.get('dataPointID', type=str)
    if data_point_id:
        query_sql = f"""
            {query_sql}
            and data_points."dataPointID"='{data_point_id}'
        """
    query_sql = _handle_time_filter(query_sql)
    records = fetch_many(query_sql)
    return records


def _modbus_capability_data(device_uid: str):
    query_sql = f"""
        SELECT
            to_char(events."msgTime", 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
            data_points."dataPointName", json.value
        FROM
            device_events events
        CROSS JOIN LATERAL
            jsonb_to_recordset(events.payload_json) as json(name text, value text)
        LEFT JOIN
            data_points on data_points."tenantID"=events."tenantID"
                and data_points."productID"=events."productID"
                and data_points."dataPointID"=json.name
        WHERE
            events."tenantID"='{g.tenant_uid}' and events."deviceID"='{device_uid}'
    """
    data_point_id = request.args.get('dataPointID', type=str)
    if data_point_id:
        query_sql = f"""
            {query_sql}
            and data_points."dataPointID"='{data_point_id}'
        """
    query_sql = _handle_time_filter(query_sql)
    records = fetch_many(query_sql)
    return records


def _lwm2m_data(device_uid: str):
    query_sql = f"""
        SELECT
            to_char(events."msgTime", 'yyyy-mm-dd HH24:MI:SS') as "msgTime",
            json.path, lwm2m_items."itemName", json.value
        FROM
            device_events events
        CROSS JOIN LATERAL
            jsonb_to_recordset(events.payload_json) as json(name text, value text, path text)
        JOIN
            lwm2m_items on lwm2m_items."objectItem"=json.name
        WHERE
            events."tenantID"='{g.tenant_uid}' and events."deviceID"='{device_uid}'
            and events.topic != 'ad/19/0/0'

    """
    path = request.args.get('path', type=str)
    if path:
        query_sql = f"""
            {query_sql}
            and lwm2m_items."objectItem"='{path}'
        """
    query_sql = _handle_time_filter(query_sql)
    records = fetch_many(query_sql)
    return records


def _handle_time_filter(query_sql: str) -> str:
    data_type = request.args.get('dataType', 'realtime')
    if data_type == 'realtime':
        time_filter_sql = f"""
            {query_sql}
                and "msgTime" >= NOW() - INTERVAL '24 HOURS'
        """
    elif data_type == 'history':
        start_time, end_time = validate_time_period_query()
        time_filter_sql = f"""
            {query_sql}
                and events."msgTime" >= '{start_time}' and events."msgTime" <= '{end_time}'
        """
    else:
        raise ParameterInvalid(field='dataType')

    time_filter_sql = f"""
        {time_filter_sql}
        ORDER BY events."msgTime" desc
    """

    return time_filter_sql
