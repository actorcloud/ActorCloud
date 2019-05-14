from flask import g

from actor_libs.database.orm import db
from actor_libs.database.sql.base import fetch_many
from actor_libs.errors import ParameterInvalid
from app.models import ApplicationGroup, GroupDevice, Application


__all__ = ['devices_event_aggr_data']


def devices_event_aggr_data(request_args):
    table_dict = {
        'hour': 'device_events_hour',
        'day': 'device_events_day',
        'month': 'device_events_month'
    }
    time_formats = {
        'hour': 'YYYY-MM-DD HH24:00',
        'day': 'YYYY-MM-DD',
        'month': 'YYYY-MM'
    }
    query_args = {
        'tenantID': g.tenant_uid,
        'table': table_dict[request_args['timeUnit']],
        'startTime': request_args['startTime'],
        'endTime': request_args['endTime'],
        'timeFormat': time_formats[request_args['timeUnit']]
    }
    if request_args.get('deviceID'):
        query_args['deviceID'] = request_args['deviceID']
        query_sql = _DEVICE_QUERY_SQL.format(**query_args)
    elif request_args.get('productID'):
        query_args['productID'] = request_args['productID']
        query_sql = _PRODUCT_QUERY_SQL.format(**query_args)
    elif request_args.get('groupID'):
        query_args['groupID'] = request_args['groupID']
        query_sql = _GROUP_QUERY_SQL.format(**query_args)
    else:
        raise ParameterInvalid(field='EventDataObject')
    if g.get('app_uid'):
        query_sql = filter_app_permission(query_sql)
    query_sql = query_sql + """ ORDER BY "countTime" DESC """  # order by
    records = fetch_many(query_sql, paginate=True)
    return records


_DEVICE_QUERY_SQL = """
SELECT 
  to_char("countTime", '{timeFormat}') AS "time",
  "deviceName", "streamName", "dataPointName",
  "minValue", "maxValue", "avgValue", "sumValue"
FROM {table}
  JOIN devices ON devices."deviceID" = {table}."deviceID" 
                  AND devices."tenantID" = {table}."tenantID"
  JOIN data_points ON data_points."dataPointID" = {table}."dataPointID"
  JOIN data_streams ON data_streams."streamID" = {table}."streamID"
WHERE {table}."countTime" between '{startTime}' AND '{endTime}'
  AND devices."deviceID" = '{deviceID}' 
  AND devices."tenantID" = '{tenantID}'
"""

_PRODUCT_QUERY_SQL = """
SELECT 
  to_char("countTime", '{timeFormat}') AS "time",
  "deviceName", "streamName", "dataPointName", "productName",
  "minValue", "maxValue", "avgValue", "sumValue"
FROM {table}
  JOIN devices ON devices."deviceID" = {table}."deviceID" 
              AND devices."tenantID" = {table}."tenantID"
  JOIN products ON devices."productID" = products."productID"
  JOIN data_points ON data_points."dataPointID" = {table}."dataPointID"
  JOIN data_streams ON data_streams."streamID" = {table}."streamID"
WHERE {table}."countTime" between '{startTime}' AND '{endTime}'
  AND devices."productID" = '{productID}'
  AND devices."tenantID" = '{tenantID}'
"""

_GROUP_QUERY_SQL = """
SELECT
  to_char("countTime", '{timeFormat}') AS "time",
  "deviceName", "streamName", "dataPointName", "groupName",
  "minValue", "maxValue", "avgValue", "sumValue"
FROM {table}
  JOIN devices ON devices."deviceID" = {table}."deviceID"
                AND devices."tenantID" = {table}."tenantID"
  JOIN groups_devices ON groups_devices."deviceIntID" = devices.id
  JOIN groups ON groups."groupID" = groups_devices."groupID"
  JOIN data_points ON data_points."dataPointID" = {table}."dataPointID"
  JOIN data_streams ON data_streams."streamID" = {table}."streamID"
WHERE {table}."countTime" between '{startTime}' AND '{endTime}'
  AND devices."tenantID" = '{groupID}'
  AND "groups"."groupID" = '{tenantID}'
"""


def filter_app_permission(query_sql):
    app_devices = db.session.query(GroupDevice.c.deviceIntID.label('id')) \
        .join(ApplicationGroup, ApplicationGroup.c.groupID == GroupDevice.c.groupID) \
        .join(Application, Application.id == ApplicationGroup.c.applicationIntID) \
        .filter(Application.appID == g.app_uid).all()
    devices_id = [device.id for device in app_devices]
    filter_sql = f"""
        AND devices.id = ANY ('{set(devices_id)}'::int[])
    """
    query_sql = query_sql + filter_sql
    return query_sql
