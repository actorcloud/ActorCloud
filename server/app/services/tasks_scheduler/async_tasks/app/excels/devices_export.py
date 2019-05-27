import pandas as pd

from actor_libs.database.async_db import db
from ._utils import pg_to_excel
from .sql_statements import dict_code_sql, query_devices_sql
from ..config import project_config


__all__ = ['devices_export_task']


async def devices_export_task(request_dict):
    """
    Export device to excel
    :return export result include status and download url
    """
    language = request_dict.get('language')
    tenant_uid = request_dict.get('tenantID')
    dict_code = {}
    dict_result = await db.fetch_many(dict_code_sql.format(language=language))
    for item in dict_result:
        dict_code[item[0]] = dict(zip(item[1], item[2]))
    column_cn = {
        'createAt': u'创建时间',
        'deviceName': u'设备名称',
        'blocked': u'是否允许访问',
        'deviceStatus': u'设备状态',
        'IMEI': u'设备IMEI',
        'IMSI': u'设备IMSI',
        'productName': u'所属产品',
        'cloudProtocol': u'云端协议',
        'authType': u'认证类型',
        'deviceID': u'设备编号',
        'deviceUsername': u'设备用户名',
        'token': u'设备秘钥',
        'softVersion': u'软件版本',
        'hardwareVersion': u'硬件版本',
        'longitude': u'经度',
        'latitude': u'纬度',
        'manufacturer': u'制造商',
        'serialNumber': u'序列号',
        'description': u'描述',
        'createUser': u'创建人'
    }
    column_sort = [
        'createAt', 'deviceName', 'productName', 'cloudProtocol', 'createUser',
        'deviceStatus', 'blocked', 'authType', 'token',
        'deviceID', 'deviceUsername', 'IMEI', 'IMSI', 'longitude', 'latitude',
        'hardwareVersion', 'serialNumber', 'softVersion', 'manufacturer',
        'description'
    ]
    query_sql = query_devices_sql
    if tenant_uid:
        query_sql += f""" where users."tenantID" = '{tenant_uid}'"""
    device_data = await db.fetch_many(query_sql)
    device_data = [dict(record) for record in device_data]
    data_frame = pd.DataFrame(device_data)[column_sort].replace(dict_code)
    if language != 'en':
        data_frame = data_frame.rename(columns=column_cn)

    export_excel_path = project_config['EXPORT_EXCEL_PATH']
    result = await pg_to_excel(
        export_excel_path, 'devices', tenant_uid, data_frame
    )
    task_result = {
        'status': result.get('status'),
        'message': 'Devices export success',
        'result': {
            'excelPath': result.get('excelPath')
        }
    }
    return task_result
