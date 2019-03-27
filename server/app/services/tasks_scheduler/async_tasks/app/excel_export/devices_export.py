import pandas as pd

from .sql_statements import dict_code_sql, devices_query_sql
from .. import project_config, postgres
from .._lib.excel import pg_to_excel

__all__ = ['export_devices']


async def export_devices(tenant_uid: str = None):
    """
    Export device to excel
    :param tenant_uid: tenant_uid
    :return export result include status and download url
    """
    dict_code_cn = dict()
    dict_result = await postgres.fetch_many(dict_code_sql)
    for item in dict_result:
        dict_code_cn[item[0]] = dict(zip(item[1], item[2]))
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
        'deviceType': u'设备类型',
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
        'deviceType', 'deviceStatus', 'blocked', 'authType', 'token',
        'deviceID', 'deviceUsername', 'IMEI', 'IMSI', 'longitude', 'latitude',
        'hardwareVersion', 'serialNumber', 'softVersion', 'manufacturer',
        'description'
    ]
    query_sql = devices_query_sql
    if tenant_uid:
        query_sql += f""" where users."tenantID" = '{tenant_uid}'"""
    device_data = await postgres.fetch_many(query_sql)
    device_data = [dict(record) for record in device_data]
    data_frame = pd.DataFrame(device_data)[column_sort] \
        .replace(dict_code_cn) \
        .rename(columns=column_cn)

    export_excel_path = project_config['EXPORT_EXCEL_PATH']
    result = await pg_to_excel(export_excel_path, 'devices', tenant_uid,
                               data_frame)
    task_result = {
        'status': result.get('status'),
        'message': 'Devices export success',
        'result': {
            'excelPath': result.get('excelPath')
        }
    }
    return task_result
