from typing import Dict, Any

import pandas as pd


__all__ = ['read_excel', 'pg_to_excel']


async def read_excel(file_path: str, rename_dict: dict = None, replace_dict: dict = None):
    """
    Read excel
    :param file_path: excel file path
    :param rename_dict: excel rename dict
    :param replace_dict: excel replace dict
    :return: dataFrame
    """
    data_frame = pd.read_excel(file_path, encoding='utf-8')
    if rename_dict:
        if len(rename_dict) != len(data_frame.columns):
            raise Exception('Excel data is not corresponding with template!')
        data_frame = data_frame[rename_dict.keys()].rename(columns=rename_dict)
    if replace_dict:
        data_frame = data_frame.replace(replace_dict)
    return data_frame


async def pg_to_excel(export_path: str, table_name: str = None, tenant_uid: str = None,
                      export_data: str = None) -> Dict[str, Any]:
    """
    Export excel to database
    :param export_path: export path
    :param table_name: database table name
    :param export_data: dataFrame in pandas
    :param tenant_uid:tenant_uid
    :return: download url
    """
    tenant_uid = tenant_uid if tenant_uid else 'admin'
    export_data.fillna('', inplace=True)
    filename = ''.join(['actorcloud', table_name, tenant_uid, '.xlsx'])
    save_excel_path = export_path + filename
    writer = pd.ExcelWriter(
        save_excel_path, datetime_format='yyyymmdd hh:mm:ss',
        engine='xlsxwriter'
    )
    export_data.to_excel(writer, index=False)
    writer.save()
    export_excel = f'download?filename={filename}&fileType=export_excel'
    task_result = {
        'status': 3,
        'excelPath': export_excel
    }
    return task_result
