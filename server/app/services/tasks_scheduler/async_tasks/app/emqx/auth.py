from datetime import datetime

from actor_libs.database.async_db import db
from .sql_statements import (
    query_base_devices_sql, device_cert_auth_sql,
    insert_connect_logs_sql, update_device_sql
)
from ..extra import HttpException


__all__ = ['device_auth']


async def device_auth(request_form):
    device_uid = request_form.get('device_id')
    cn = request_form.get('cn')
    connect_date = str(datetime.now())
    if cn and cn != 'undefined':
        query_sql = device_cert_auth_sql.format(
            deviceID=device_uid, CN=cn
        )
        auth_type = 2
    else:
        query_sql = query_base_devices_sql.format(
            deviceID=device_uid
        )
        auth_type = 1
    query_result = await db.fetch_row(query_sql)
    if not query_result:
        raise HttpException(404, field='device')
    device_info = dict(query_result)
    if auth_type != device_info['authType']:
        raise HttpException(404, field='authType')
    if device_info['protocol'] == 'lwm2m' or auth_type == 2:
        auth_status = True
    elif all([auth_type == 1,
              device_info['deviceUsername'] == request_form.get('username'),
              device_info['token'] == request_form.get('password')]):
        auth_status = True
    else:
        auth_status = False
    connect_dict = {
        'IP': request_form.get('ip'),
        'msgTime': connect_date,
        'deviceID': device_info['deviceID'],
        'tenantID': device_info['tenantID']
    }
    if auth_status:
        connect_dict['connectStatus'] = 1
        mountpoint = (
            f"/{device_info['protocol']}/{device_info['tenantID']}"
            f"/{device_info['productID']}/{device_info['deviceID']}/"
        )
        record, code = {'mountpoint': mountpoint}, 200
    else:
        connect_dict['connectStatus'] = 2
        record, code = {'status': 401}, 401
    await db.execute(insert_connect_logs_sql.format(**connect_dict))
    await db.execute(
        update_device_sql.format(
            lastConnection=connect_date,
            deviceStatus=1,
            deviceID=device_info['deviceID']
        ))
    return record, code
