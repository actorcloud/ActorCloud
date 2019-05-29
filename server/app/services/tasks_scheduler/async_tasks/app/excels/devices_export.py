import pandas as pd

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import update_task
from ._utils import pg_to_excel
from .multi_language import EXPORT_RENAME_ZH
from .sql_statements import dict_code_sql, end_devices_export_sql
from ..config import project_config


__all__ = ['devices_export_task']


async def devices_export_task(request_dict):
    """
    Export device to excel
    :return export result include status and download url
    """

    task_id = request_dict['taskID']
    language = request_dict.get('language')
    tenant_uid = request_dict.get('tenantID')
    dict_code = {}
    dict_result = await db.fetch_many(dict_code_sql.format(language=language))
    for item in dict_result:
        dict_code[item[0]] = dict(zip(item[1], item[2]))
    column_sort = list(EXPORT_RENAME_ZH.keys())
    query_sql = end_devices_export_sql
    if tenant_uid:
        query_sql += f""" where users."tenantID" = '{tenant_uid}'"""
    device_data = await db.fetch_many(query_sql)
    device_data = [dict(record) for record in device_data]
    data_frame = pd.DataFrame(device_data)[column_sort].replace(dict_code)
    if language != 'en':
        data_frame = data_frame.rename(columns=EXPORT_RENAME_ZH)
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
    await update_task(task_id, update_dict=task_result)
