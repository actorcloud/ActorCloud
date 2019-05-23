import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, AnyStr

import pandas as pd

from actor_libs.database.async_db import db
from actor_libs.tasks.sql_statement import update_task_sql
from ._utils import pg_to_excel
from ._utils import read_excel
from .multi_language import (
    ImportStatus, STATUS_MESSAGE, IMPORT_RENAME_ZH, EXPORT_RENAME
)
from .sql_statements import (
    dict_code_sql, query_tenant_devices_limit_sql
)
from .validate import validates_schema
from ..config import project_config


async def import_devices(request_json):
    """
    {'taskID', 'language', 'filePath', 'tenantID', 'userIntID'}
    """

    task_id = request_json['taskID']
    await _update_import_progress(
        task_id, status=2, progress=10,
        import_status=ImportStatus.UPLOADED
    )
    dict_code = await get_dict_code(request_json['language'])
    import_records, task_result = await read_devices_excels(
        request_json, dict_code
    )
    if not import_records and task_result:
        # todo excel empty ?
        return task_result
    correct_records, error_records = await handle_import_records(
        import_records, request_json
    )
    correct_num, error_nums = len(correct_records), len(error_records)
    result_info = {
        'success': correct_num,
        'failed': error_nums
    }
    if correct_num > 0:
        await _import_correct_rows(correct_records, correct_num, request_json)
    if error_records:
        try:
            export_path = await _export_error_rows(
                error_records, dict_code, request_json
            )
        except Exception as e:
            export_path = None
        result_info['excelPath'] = export_path
    await _update_import_progress(
        task_id,
        status=3,
        progress=100,
        import_status=ImportStatus.COMPLETED,
        result=result_info
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


async def read_devices_excels(request_json: Dict, dict_code):
    language = request_json['language']
    try:
        rename_dict = IMPORT_RENAME_ZH if language != 'en' else None
        data_frame = await read_excel(
            request_json['filePath'], rename_dict=rename_dict,
            replace_dict=dict_code
        )
        data_frame = await _handle_data_frame(data_frame)
        import_records = data_frame.to_dict('records')
        await _update_import_progress(
            request_json['taskID'], status=2,
            progress=30, import_status=ImportStatus.READING
        )
        task_result = {}
    except Exception as e:
        # todo log and raise exception
        import_records = {}
        task_result = await _update_import_progress(
            request_json['taskID'], status=4,
            progress=35, import_status=ImportStatus.TEMPLATE_ERROR
        )
    return import_records, task_result


async def _handle_data_frame(data_frame):
    cover_float = ['longitude', 'latitude']
    data_frame[cover_float] = data_frame[cover_float].astype(float)
    # nan -> None
    data_frame = data_frame.where((pd.notnull(data_frame)), None)
    imei = data_frame['IMEI'].astype(str)
    data_frame['IMEI'] = imei.mask(imei == 'None', None)
    return data_frame


async def handle_import_records(import_records, request_json):
    # use schema to validate imported data
    try:
        validated_result = await validates_schema(
            import_records, request_json
        )
        await _update_import_progress(
            request_json['taskID'], status=2, progress=50,
            import_status=ImportStatus.VALIDATING
        )
    except Exception as e:
        task_result = await _update_import_progress(
            request_json['taskID'], status=4, progress=55,
            import_status=ImportStatus.ABNORMAL
        )
        return task_result
    rows_error_msg, devices_attr_info = validated_result
    products_info = devices_attr_info['products_info']
    gateways_info = devices_attr_info['gateways_info']

    correct_records = []
    correct_record_append = correct_records.append
    error_records = []
    error_record_append = error_records.append
    for row, record in enumerate(import_records):
        if rows_error_msg.get(row):
            record.update(rows_error_msg[row])
            error_record_append(record)
        else:
            record['productID'] = products_info.get(record['product'])
            record['gateway'] = gateways_info.get(record['gateway'])
            correct_record_append(record)
    return correct_records, error_records


async def _import_correct_rows(correct_records, correct_num, request_json):
    is_exceed_limit = _check_devices_limit(correct_num, request_json)
    if is_exceed_limit:
        await _update_import_progress(
            request_json['taskID'], status=4, progress=70,
            import_status=ImportStatus.LIMITED
        )
        return
    try:
        await _insert_correct_rows(correct_records, request_json)
        await _update_import_progress(
            request_json['taskID'], status=4,
            progress=80, import_status=ImportStatus.IMPORTING
        )
    except Exception as e:
        await _update_import_progress(
            request_json['taskID'], status=4,
            progress=85, import_status=ImportStatus.FAILED
        )


async def _check_devices_limit(correct_num, request_json) -> bool:
    """
    Check if the device limit is exceeded
    :return True if exceed limit otherwise False
    """

    check_status = False
    query_sql = query_tenant_devices_limit_sql.format(
        tenantID=request_json['tenantID']
    )
    query_result = await db.fetch_row(query_sql)
    device_sum, devices_limit = query_result
    if device_sum + correct_num > devices_limit:
        return True
    return check_status


async def _insert_correct_rows(correct_records, request_json):
    default_columns = [
        "createAt", "deviceName", "deviceType", "productID",
        "authType", "upLinkNetwork", "deviceID", "deviceUsername", "token",
        "location", "latitude", "longitude",
        "manufacturer", "serialNumber", "softVersion", "hardwareVersion",
        "deviceConsoleIP", "deviceConsoleUsername", "deviceConsolePort",
        "mac", "upLinkSystem", "gateway", "parentDevice",
        "loraData", "lwm2mData", "modbusData",
        "userIntID", "tenantID"
    ]
    create_at = datetime.now()
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            for record in correct_records:
                record['createAt'] = create_at
                record['userIntID'] = request_json['userIntID']
                record['tenantID'] = request_json['tenantID']
                miss_columns = set(default_columns) - set(record.keys())
                record.update({c: 'NULL' for c in miss_columns})
                execute_sql = import_devices(**record)
                await conn.execute(execute_sql)


async def _export_error_rows(errors_rows, dict_code, request_json):
    """ Export processing failure data to excel """

    column_sort = [
        'deviceName', 'authType', 'product', 'IMEI',
        'upLinkSystem', 'gateway', 'upLinkNetwork',
        'deviceID', 'deviceUsername', 'token',
        'longitude', 'latitude', 'location', 'softVersion',
        'hardwareVersion', 'manufacturer', 'serialNumber',
        'description', 'autoSub'
    ]
    error_dict_code = defaultdict(dict)
    for code, code_value in dict_code.items():
        for code_k, code_v in code_value.items():
            error_dict_code[code][code_v] = code_k
    data_frame = pd.DataFrame(errors_rows)
    data_frame = data_frame[column_sort].replace(error_dict_code)
    if request_json['language'] != 'en':
        data_frame = data_frame.rename(columns=EXPORT_RENAME)
    state_dict = await pg_to_excel(
        export_path=project_config.get('EXPORT_EXCEL_PATH'),
        table_name='ErrorImportDevicesW5',
        export_data=data_frame,
        tenant_uid=request_json['tenantID'])
    export_path = state_dict.get('excelPath')
    return export_path


async def _update_import_progress(task_id,
                                  *,
                                  status=None,
                                  progress=None,
                                  import_status=None,
                                  **kwargs):
    result = kwargs.get('result', None)
    result['message'] = STATUS_MESSAGE.get(import_status)
    result['code'] = import_status.value
    update_dict = {
        'updateAt': datetime.now(),
        'taskStatus': status,
        'taskProgress': progress,
        'taskResult': json.dumps(result),
        'taskID': task_id
    }
    update_sql = update_task_sql.format(**update_dict)
    await db.execute(update_sql)
    return result
