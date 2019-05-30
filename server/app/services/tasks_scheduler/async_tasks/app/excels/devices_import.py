import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, AnyStr

import pandas as pd

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import update_task
from actor_libs.tasks.exceptions import TaskException
from actor_libs.utils import generate_uuid
from ._utils import pg_to_excel
from ._utils import read_excel
from .multi_language import (
    ImportStatus, STATUS_MESSAGE, IMPORT_RENAME_ZH, IMPORT_ERROR_RENAME
)
from .sql_statements import (
    device_import_sql, dict_code_sql,
    query_tenant_devices_limit_sql,
)
from .validate import validates_schema
from ..config import project_config


__all__ = ['devices_import_task']


logger = logging.getLogger(__name__)


async def devices_import_task(request_dict):
    """
    {'taskID', 'language', 'filePath', 'tenantID', 'userIntID'}
    """

    task_id = request_dict['taskID']
    await _update_task_progress(
        task_id, status=2, progress=10,
        import_status=ImportStatus.UPLOADED
    )
    dict_code = await get_dict_code(request_dict['language'])
    import_records = await read_devices_excels(
        request_dict, dict_code
    )
    if not import_records:
        await _update_task_progress(
            request_dict['taskID'], status=4,
            progress=15, import_status=ImportStatus.FAILED
        )
        raise TaskException(code=500, error_code='FAILED')
    correct_records, error_records = await handle_import_records(
        import_records, request_dict
    )
    correct_num, error_nums = len(correct_records), len(error_records)
    result_info = {
        'success': correct_num,
        'failed': error_nums
    }
    if correct_num > 0:
        await _import_correct_rows(correct_records, correct_num, request_dict)
    if error_records:
        try:
            export_path = await _export_error_rows(
                error_records, dict_code, request_dict
            )
            result_info['excelPath'] = export_path
        except Exception as e:
            logger.error(f"error_records: {e}")
    await _update_task_progress(
        request_dict['taskID'], status=3,
        progress=100, import_status=ImportStatus.COMPLETED,
        result=result_info,
    )


async def get_dict_code(language: AnyStr) -> Dict:
    dict_code = {}
    query_dict_code = await db.fetch_many(
        dict_code_sql.format(language=language)
    )
    for item in query_dict_code:
        # {code:{label:value}...}
        dict_code[item[0]] = dict(zip(item[2], item[1]))
    return dict_code


async def read_devices_excels(request_dict: Dict, dict_code):
    try:
        rename_dict = IMPORT_RENAME_ZH if request_dict['language'] != 'en' else None
        data_frame = await read_excel(
            request_dict['filePath'], rename_dict=rename_dict,
            replace_dict=dict_code
        )
        data_frame = await _handle_data_frame(data_frame)
        import_records = data_frame.to_dict('records')
        await _update_task_progress(
            request_dict['taskID'], status=2,
            progress=30, import_status=ImportStatus.READING
        )
    except Exception as e:
        logger.error(f"read_devices_excels: {e}")
        await _update_task_progress(
            request_dict['taskID'], status=4,
            progress=35, import_status=ImportStatus.TEMPLATE_ERROR
        )
        raise TaskException(code=500, error_code='TEMPLATE_ERROR')
    return import_records


async def _handle_data_frame(data_frame):
    cover_float = ['longitude', 'latitude']
    data_frame[cover_float] = data_frame[cover_float].astype(float)
    # nan -> None
    data_frame = data_frame.where((pd.notnull(data_frame)), None)
    return data_frame


async def handle_import_records(import_records, request_dict):
    # use schema to validate imported data

    correct_records = []
    correct_record_append = correct_records.append
    error_records = []
    error_record_append = error_records.append
    try:
        validated_result = await validates_schema(
            import_records, request_dict
        )
        await _update_task_progress(
            request_dict['taskID'], status=2, progress=50,
            import_status=ImportStatus.VALIDATING
        )
    except Exception as e:
        logger.error(f"validates_schema: {e}")
        await _update_task_progress(
            request_dict['taskID'], status=4, progress=55,
            import_status=ImportStatus.ABNORMAL
        )
        raise TaskException(code=500, error_code='ABNORMAL')
    rows_error_msg, devices_attr_info = validated_result
    products_info = devices_attr_info['products_info']
    gateways_info = devices_attr_info['gateways_info']

    for row, record in enumerate(import_records):
        if rows_error_msg.get(row):
            record.update(rows_error_msg[row])
            error_record_append(record)
        else:
            product_name = record['product']
            gateway_name = record['gateway']
            if products_info.get(product_name):
                record['productID'] = products_info[product_name]['productID']
                record['cloudProtocol'] = products_info[product_name]['cloudProtocol']
            if gateways_info.get(gateway_name):
                record['gateway'] = gateways_info[gateway_name]['id']
            record = await set_device_default_value(record)
            correct_record_append(record)
    return correct_records, error_records


async def _import_correct_rows(correct_records, correct_num, request_dict):
    is_exceed_limit = await _check_devices_limit(correct_num, request_dict)
    if is_exceed_limit:
        await _update_task_progress(
            request_dict['taskID'], status=4, progress=70,
            import_status=ImportStatus.LIMITED
        )
        raise TaskException(code=500, error_code='LIMITED')
    try:
        await _insert_correct_rows(correct_records, request_dict)
        await _update_task_progress(
            request_dict['taskID'], status=2,
            progress=80, import_status=ImportStatus.IMPORTING
        )
    except Exception as e:
        logger.error(f"_import_correct_rows: {e}")
        await _update_task_progress(
            request_dict['taskID'], status=4,
            progress=85, import_status=ImportStatus.FAILED
        )
        raise TaskException(code=500, error_code='FAILED')


async def _check_devices_limit(correct_num, request_dict) -> bool:
    """
    Check if the device limit is exceeded
    :return True if exceed limit otherwise False
    """

    check_status = False
    query_sql = query_tenant_devices_limit_sql.format(
        tenantID=request_dict['tenantID']
    )
    query_result = await db.fetch_row(query_sql)
    if query_result:
        device_sum, devices_limit = query_result
        if device_sum + correct_num > devices_limit:
            check_status = True
    return check_status


async def _insert_correct_rows(correct_records, request_dict):
    default_columns = [
        "createAt", "deviceName", "deviceType", "productID",
        "authType", "upLinkNetwork", "deviceID", "deviceUsername", "token",
        "location", "latitude", "longitude",
        "manufacturer", "serialNumber", "softVersion", "hardwareVersion",
        "deviceConsoleIP", "deviceConsoleUsername", "deviceConsolePort",
        "mac", "upLinkSystem", "gateway", "parentDevice",
        "loraData", "lwm2mData", "userIntID", "tenantID"
    ]
    create_at = datetime.now()
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            for record in correct_records:
                record['createAt'] = create_at
                record['userIntID'] = request_dict['userIntID']
                record['tenantID'] = request_dict['tenantID']
                miss_columns = set(default_columns) - set(record.keys())
                record.update({c: None for c in miss_columns})
                execute_sql = device_import_sql.format(**record)
                execute_sql = execute_sql.replace("'None'", "NULL")
                execute_sql = execute_sql.replace("'NULL'", "NULL")
                await conn.execute(execute_sql)


async def _export_error_rows(errors_rows, dict_code, request_dict):
    """ Export processing failure data to excel """

    column_sort = list(IMPORT_ERROR_RENAME.keys())
    error_dict_code = defaultdict(dict)
    for code, code_value in dict_code.items():
        for code_k, code_v in code_value.items():
            error_dict_code[code][code_v] = code_k
    data_frame = pd.DataFrame(errors_rows)
    data_frame = data_frame[column_sort].replace(error_dict_code)
    if request_dict['language'] != 'en':
        data_frame = data_frame.rename(columns=IMPORT_ERROR_RENAME)
    state_dict = await pg_to_excel(
        export_path=project_config.get('EXPORT_EXCEL_PATH'),
        table_name='ErrorImportDevicesW5',
        export_data=data_frame,
        tenant_uid=request_dict['tenantID'])
    export_path = state_dict.get('excelPath')
    return export_path


async def set_device_default_value(device_info):
    if device_info.get('upLinkSystem') != 3:
        device_info['gateway'] = None
    if device_info.get('upLinkSystem') == 3 and not device_info.get('gateway'):
        device_info['upLinkSystem'] = 1
        device_info['gateway'] = None
    if device_info.get('cloudProtocol') == 3:
        # lwm2m protocol
        if device_info.get('deviceID'):
            imei = device_info['deviceID']
        else:
            imei = generate_uuid(size=15)
            device_info['deviceID'] = imei
        lwm2m_data = {
            'autoSub': 0,
            'IMEI': imei,
            'IMSI': imei
        }
        device_info['lwm2mData'] = json.dumps(lwm2m_data)
    if not device_info.get('deviceID'):
        device_info['deviceID'] = generate_uuid()
    if not device_info.get('deviceUsername'):
        device_info['deviceUsername'] = generate_uuid()
        if not device_info.get('token'):
            device_info['token'] = device_info['deviceUsername']
    if not device_info.get('token'):
        device_info['token'] = device_info['deviceUsername']
    device_info['upLinkNetwork'] = 1
    device_info['deviceType'] = 1  # end_devices
    return device_info


async def _update_task_progress(task_id,
                                *,
                                status=None,
                                progress=None,
                                import_status=None,
                                result=None):
    if not result:
        result = {}
    result['message'] = STATUS_MESSAGE.get(import_status)
    result['code'] = import_status.value
    update_dict = {
        'status': status,
        'progress': progress,
        'result': result,
        'taskID': task_id
    }
    await update_task(task_id, update_dict)
    return result
