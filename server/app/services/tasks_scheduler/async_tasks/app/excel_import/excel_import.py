import logging
import re
from collections import defaultdict
from datetime import datetime

import json
import pandas as pd
from marshmallow import Schema, ValidationError
from marshmallow.validate import OneOf

from actor_libs.schemas.fields import EmqString, EmqInteger, EmqFloat
from actor_libs.tasks.task import update_task
from actor_libs.utils import generate_uuid
from .multi_language import (
    ImportStatus, STATUS_MESSAGE, get_row_error_message, Error, IMPORT_RENAME, EXPORT_RENAME
)
from .sql_statements import (
    dict_code_sql, query_device_count_sql, query_device_sum_sql, query_devices_name_sql,
    query_device_by_username_sql, query_product_sql, query_device_by_uid_sql,
    query_gateway_sql, query_sub_sql, query_column_default, insert_device_sql,
    insert_sub_sql, query_device_by_product_sql, query_device_by_imei_sql
)
from .. import project_config, postgres
from .._lib.excel import read_excel, pg_to_excel


__all__ = ['ImportDevices']

logger = logging.getLogger(__name__)


def validate_uid(value):
    """
    Validate device_uid,username,password
    """
    if value and not re.match(r"^[0-9a-zA-Z_]{8,36}$", value):
        raise ValidationError('error format')


class ImportDeviceSchema(Schema):
    deviceName = EmqString(required=True)
    product = EmqString(required=True)  # productName
    authType = EmqInteger(required=True, validate=OneOf([1, 2]))
    upLinkSystem = EmqInteger(required=True, validate=OneOf([1, 2]))
    deviceID = EmqString(allow_none=True, validate=validate_uid)
    deviceUsername = EmqString(allow_none=True, validate=validate_uid)
    token = EmqString(allow_none=True, validate=validate_uid)
    longitude = EmqFloat(allow_none=True)
    latitude = EmqFloat(allow_none=True)
    location = EmqString(allow_none=True)
    serialNumber = EmqString(allow_none=True, len_max=100)
    deviceConsoleIP = EmqString(allow_none=True)
    deviceConsoleUsername = EmqString(allow_none=True)
    deviceConsolePort = EmqInteger(allow_none=True)
    softVersion = EmqString(allow_none=True)
    hardwareVersion = EmqString(allow_none=True)
    manufacturer = EmqString(allow_none=True)
    description = EmqString(allow_none=True, len_max=300)
    gateway = EmqString(allow_none=True)  # gateway(deviceName)
    modBusIndex = EmqInteger(allow_none=True)  # for Modbus
    IMEI = EmqString(allow_none=True, len_max=15)
    autoSub = EmqInteger(allow_none=True, validate=OneOf([0, 1]))


class ImportDevices:
    def __init__(self, task_kwargs=None):
        """
        :param task_kwargs {'userIntID', 'language', 'tenantID', 'filePath', 'taskID'}
        """
        self.task_kwargs = task_kwargs
        self.tenant_uid = task_kwargs.get('tenantID')
        self.user_id = task_kwargs.get('userIntID')
        self.task_id = task_kwargs.get('taskID')
        self.dict_code = {}
        self.rows_errors_msg = {}
        self.errors_rows_number = []
        self.product_name_uid = {}  # {productName: productID}
        self.product_name_protocol = {}  # {productName: protocol}
        self.device_name_id = {}  # {deviceName: id}
        self.task_result = {}
        self.language = None

    async def import_excel(self):

        await self._update_task_status(status=2, progress=10, import_status=ImportStatus.UPLOADED)

        file_path = self.task_kwargs.get('filePath')
        self.language = self.task_kwargs.get('language')
        dict_result = await postgres.fetch_many(dict_code_sql.format(language=self.language))
        for item in dict_result:
            # {code:{label:value}...}
            self.dict_code[item[0]] = dict(zip(item[2], item[1]))

        try:
            await self._update_task_status(
                status=2, progress=30, import_status=ImportStatus.READING)
            rename_dict = None
            if self.language != 'en':
                rename_dict = IMPORT_RENAME
            data_frame = await read_excel(
                file_path, rename_dict=rename_dict, replace_dict=self.dict_code)
            data_frame = self._handle_data_frame(data_frame)
            import_records = data_frame.to_dict('records')
        except Exception as e:
            logger.error(str(e))
            await self._update_task_status(
                status=4, progress=35, import_status=ImportStatus.TEMPLATE_ERROR)
            return self.task_result

        try:
            await self._update_task_status(
                status=2, progress=50, import_status=ImportStatus.VALIDATING)
            await self._schema_validate(import_records=import_records)
        except Exception as e:
            logger.error(str(e))
            await self._update_task_status(
                status=4, progress=55, import_status=ImportStatus.ABNORMAL)
            return self.task_result

        insert_pg_record = []
        insert_pg_append = insert_pg_record.append
        export_excel_record = []
        export_excel_append = export_excel_record.append
        for row, record in enumerate(import_records):
            if self.rows_errors_msg.get(row):
                record.update(self.rows_errors_msg.get(row))
                export_excel_append(record)
            else:
                insert_pg_append(record)

        is_exceed_limit = await self._check_devices_limit(len(insert_pg_record))
        if is_exceed_limit:
            await self._update_task_status(
                status=4, progress=70, import_status=ImportStatus.LIMITED)
            return self.task_result

        try:
            await self._update_task_status(
                status=2, progress=80, import_status=ImportStatus.IMPORTING)
            await self._insert_devices_pg(insert_pg_record)
        except Exception as e:
            logger.error(str(e))
            await self._update_task_status(
                status=4, progress=85, import_status=ImportStatus.FAILED)
            return self.task_result
        result_info = {
            'success': len(insert_pg_record),
            'failed': len(export_excel_record)
        }
        await self._update_task_status(
            status=3,
            progress=100,
            import_status=ImportStatus.COMPLETED,
            result=result_info)
        if export_excel_record:
            try:
                error_path = await self._export_error_devices(export_excel_record)
                result_info['excelPath'] = error_path
                await self._update_task_status(
                    status=3,
                    progress=100,
                    import_status=ImportStatus.COMPLETED,
                    result=result_info)
            except Exception as e:
                logger.error(str(e))
                await self._update_task_status(
                    status=3,
                    progress=100,
                    import_status=ImportStatus.COMPLETED,
                    result=result_info)
                return self.task_result
        return self.task_result

    @staticmethod
    def _handle_data_frame(data_frame):
        cover_float = ['longitude', 'latitude']
        data_frame[cover_float] = data_frame[cover_float].astype(float)
        # nan -> None
        data_frame = data_frame.where((pd.notnull(data_frame)), None)
        imei = data_frame['IMEI'].astype(str)
        data_frame['IMEI'] = imei.mask(imei == 'None', None)
        return data_frame

    async def _export_error_devices(self, records):
        """ Export error devices to excel """

        column_sort = [
            'deviceName', 'authType', 'product', 'upLinkSystem',
            'IMEI', 'modBusIndex', 'gateway', 'deviceID', 'deviceUsername',
            'token', 'longitude', 'latitude', 'location', 'softVersion',
            'hardwareVersion', 'manufacturer', 'serialNumber', 'description',
            'autoSub'
        ]
        dict_code = defaultdict(dict)
        for code, code_value in self.dict_code.items():
            for k, v in code_value.items():
                dict_code[code][v] = k
        data_frame = pd.DataFrame(records)
        data_frame = data_frame[column_sort].replace(dict_code)
        if self.language != 'en':
            data_frame = data_frame.rename(columns=EXPORT_RENAME)
        state_dict = await pg_to_excel(
            export_path=project_config.get('EXPORT_EXCEL_PATH'),
            table_name='ErrorImportDevicesW5',
            export_data=data_frame,
            tenant_uid=self.tenant_uid)
        export_path = state_dict.get('excelPath')
        return export_path

    async def _insert_devices_pg(self, records):

        default_value_dict = {}
        device_default = await postgres.fetch_many(query_column_default)
        default_value_dict.update(dict(device_default))

        data_now = datetime.now()
        add_devices = []
        add_device_append = add_devices.append
        execute_sql = ''
        for i, record in enumerate(records):
            # TODO 网关导入
            device = {
                'createAt': data_now,
                'tenantID': self.tenant_uid,
                'userIntID': self.user_id,
                'type': 1
            }
            product = record.get('product')
            protocol = self.product_name_protocol.get(product)
            if protocol == 3:
                # Lwm2m,assign IMEI to deviceID and deviceUsername
                record['deviceID'] = record.get('IMEI')
                record['deviceUsername'] = record.get('IMEI')
                record['autoSub'] = record.get('autoSub', 0)
            for key, value in record.items():
                if key in ['deviceID', 'deviceUsername', 'token'] and not value:
                    value = generate_uuid()
                if key == 'product' and self.product_name_uid.get(value):
                    device['productID'] = self.product_name_uid.get(value)
                elif key == 'gateway' and self.device_name_id.get(value):
                    device['gateway'] = self.device_name_id.get(value)
                elif key in default_value_dict:
                    device[key] = value if value else 'NULL'
                else:
                    continue
            miss_columns = set(default_value_dict.keys()) - set(device.keys())
            for column in miss_columns:
                default_value = default_value_dict.get(column)
                if default_value is None:
                    default_value = 'NULL'
                device[column] = default_value
            device['client'] = f'client{i}'
            add_device_append(device)
            execute_sql += insert_device_sql.format(**device)
        if not add_devices:
            return

        await execute_with_transaction(execute_sql)
        await self._device_product_sub()

    async def _check_devices_limit(self, add_device_count) -> bool:
        """
        Check if the device limit is exceeded
        :param add_device_count: count of devices to be imported
        :return True if exceed limit otherwise False
        """
        tenant_devices_limit = await postgres.fetch_row(
            query_device_count_sql.format(tenantID=self.tenant_uid))
        tenant_devices_limit = tenant_devices_limit[0]
        if not tenant_devices_limit or tenant_devices_limit <= 0:
            return False

        device_count = await postgres.fetch_row(
            query_device_sum_sql.format(tenantID=self.tenant_uid))
        device_count = device_count[0]
        if device_count + add_device_count > tenant_devices_limit:
            return True
        return False

    async def _device_product_sub(self):
        """ Proxy sub """
        products_uid = ','.join(self.product_name_uid.values())
        query = await postgres.fetch_many(
            query_sub_sql.format(products_uid=products_uid))
        if not query:
            return
        products_sub = {}
        for record in query:
            products_sub[record['productID']] = {
                'topic': record['topic'],
                'qos': record['qos']
            }

        execute_sql = ''
        devices_query = await postgres.fetch_many(
            query_device_by_product_sql.format(products_uid=products_uid))

        for device in devices_query:
            product_uid = device['productID']
            if products_sub.get(product_uid):
                sub = products_sub.get(product_uid)
                mqtt_sub = {
                    'createAt': datetime.now(),
                    'clientID': device['client_id'],
                    'topic': sub['topic'],
                    'qos': sub['qos'],
                    'deviceIntID': device['id']
                }
                execute_sql += insert_sub_sql.format(**mqtt_sub)
        await execute_with_transaction(execute_sql)

    async def _schema_validate(self, import_records=None):
        """ Validate with schema """

        validated_schema = ImportDeviceSchema(many=True).load(import_records)
        _schema_validate_data = validated_schema.data
        handle_errors_msg = validated_schema.errors
        for row, info in handle_errors_msg.items():
            for column, _ in info.items():
                handle_errors_msg[row][column] = self.get_error_msg(Error.FORMAT_ERROR)
        self.rows_errors_msg.update(handle_errors_msg)
        self.errors_rows_number.extend(handle_errors_msg.keys())

        rows_device_name = {}  # 校验设备名(唯一性 租户)
        rows_product = {}  # 校验产品名(是否存在 租户)
        rows_modbus_index = {}  # 校验索引( Modbus协议 产品)
        rows_device_uid = {}  # 设备uid(唯一性 租户)
        rows_device_info = {}  # 校验设备名, 用户名，密码(唯一性 平台)
        rows_uplink_system = {}  # 配合网关的检验
        rows_gateway = {}  # 校验网关(是否存在 租户)
        rows_imei = {}
        for row, value in enumerate(_schema_validate_data):
            if row in self.errors_rows_number:
                continue
            rows_device_name[row] = value.get('deviceName')
            rows_product[row] = value.get('product')
            rows_modbus_index[row] = value.get('modBusIndex')
            rows_uplink_system[row] = value.get('upLinkSystem')
            rows_gateway[row] = value.get('gateway')
            rows_imei[row] = value.get('IMEI')
            if value.get('deviceID'):
                rows_device_uid[row] = value.get('deviceID')
                if value.get('deviceUsername') and value.get('token'):
                    rows_device_info[row] = [
                        value.get('deviceID'),
                        value.get('deviceUsername')
                    ]
        await self._validate_devices_name(rows_device_name=rows_device_name)
        await self._validate_products_name(
            rows_product=rows_product, rows_modbus_index=rows_modbus_index)
        await self._validate_device_uid(rows_device_uid=rows_device_uid)
        await self._validate_device_info(rows_device_info=rows_device_info)
        await self._validate_gateway(
            rows_uplink_system=rows_uplink_system, rows_gateway=rows_gateway)
        await self._validate_device_imei(
            rows_product=rows_product, rows_devices_imei=rows_imei)

    async def _validate_devices_name(self, rows_device_name):
        """
        Validate device name is unique
        :param rows_device_name: dict {row_id: deviceName}
        """
        rows_error_msg = {}
        validate_names = []
        for row, value in rows_device_name.items():
            if value in validate_names:
                rows_error_msg[row] = {
                    'deviceName':
                        self.get_error_msg(Error.DEVICE_NAME_DUPLICATE) %
                        rows_device_name.pop(row)
                }
            else:
                validate_names.append(value)

        if validate_names:
            devices_name = ','.join(validate_names)
            query = await postgres.fetch_many(
                query_devices_name_sql.format(
                    devices_name=devices_name, tenantID=self.tenant_uid))
            query_names = [i[0] for i in query]
            for row, name in rows_device_name.items():
                if name in query_names:
                    rows_error_msg[row] = {
                        'deviceName':
                            self.get_error_msg(Error.DEVICE_NAME_DUPLICATE) % name
                    }
        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _validate_products_name(self, rows_product, rows_modbus_index):
        """
        Validate if product name is exist
        :param rows_product: dict {row_id: productName}
        :param rows_modbus_index: dict {row_id: modBusIndex}
        """

        rows_error_msg = {}
        for row, name in list(rows_product.items()):
            if row in self.errors_rows_number:
                del rows_product[row]
                continue

        if rows_product.values():
            products_name = ','.join(rows_product.values())
            query = await postgres.fetch_many(
                query_product_sql.format(
                    products_name=products_name, tenantID=self.tenant_uid))
            product_uid_dict = {}
            product_protocol_dict = {}
            for record in query:
                product_name = record['productName']
                product_uid_dict[product_name] = record['productID']
                product_protocol_dict[product_name] = record['cloudProtocol']

            for row, name in rows_product.items():
                if not product_uid_dict.get(name):
                    rows_error_msg[row] = {
                        'product': self.get_error_msg(Error.PRODUCT_NOT_EXIST) % name
                    }
            self.product_name_uid = product_uid_dict
            self.product_name_protocol = product_protocol_dict

            for row, name in rows_product.items():
                if product_protocol_dict.get(
                        name) == 7 and not rows_modbus_index[row]:
                    rows_error_msg[row] = {
                        'modBusIndex': self.get_error_msg(Error.INDEX_REQUIRED)
                    }
                elif product_protocol_dict.get(
                        name) != 7 and rows_modbus_index[row]:
                    rows_error_msg[row] = {
                        'modBusIndex':
                            self.get_error_msg(Error.INDEX_NOT_REQUIRED) %
                            rows_modbus_index[row]
                    }
                elif rows_modbus_index[row] and rows_modbus_index[row] not in range(0, 256):
                    rows_error_msg[row] = {
                        'modBusIndex':
                            self.get_error_msg(Error.INDEX_INVALID) %
                            rows_modbus_index[row]
                    }

        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _validate_device_uid(self, rows_device_uid):
        """
        Validate if device_uid is unique
        :param rows_device_uid: dict {row_id: deviceID}
        :return: rows_error_msg: error row and error message
        """

        rows_error_msg = {}
        devices_uid = []
        for row, value in list(rows_device_uid.items()):
            if row in self.errors_rows_number:
                del rows_device_uid[row]
                continue
            if value in devices_uid:
                rows_error_msg[row] = {
                    'deviceID':
                        self.get_error_msg(Error.DEVICE_ID_DUPLICATE) %
                        rows_device_uid.pop(row)
                }
            else:
                devices_uid.append(value)

        if devices_uid:
            devices_uid = ','.join(devices_uid)
            query = await postgres.fetch_many(
                query_device_by_uid_sql.format(
                    devices_uid=devices_uid, tenantID=self.tenant_uid))
            query_uids = [i[0] for i in query]
            for row, uid in rows_device_uid.items():
                if uid in query_uids:
                    rows_error_msg[row] = {
                        'deviceID': self.get_error_msg(Error.DEVICE_ID_DUPLICATE) % uid
                    }
        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _validate_device_info(self, rows_device_info):
        """
        Validate device base info is unique: deviceID, deviceUsername, token
        :param rows_device_info: dict {row_id: (deviceID, deviceUsername, token)}
        """

        rows_error_msg = {}
        devices_info = []
        for row, info in list(rows_device_info.items()):
            if row in self.errors_rows_number:
                del rows_device_info[row]
                continue
            if info in devices_info:
                del rows_device_info[row]
                rows_error_msg[row] = {
                    'deviceID': self.get_error_msg(Error.DEVICE_ID_DUPLICATE)[:-4],
                    'deviceUsername': self.get_error_msg(Error.DEVICE_USERNAME_DUPLICATE)[:-4]
                }
            else:
                devices_info.append(tuple(info))

        if devices_info:
            query_info = await postgres.fetch_many(
                query_device_by_username_sql.format(
                    devices=tuple(devices_info)))
            for rows, info in rows_device_info.items():
                info = tuple(info)
                if info in query_info:
                    rows_error_msg[rows] = {
                        'deviceID': self.get_error_msg(Error.DEVICE_ID_DUPLICATE)[:-4],
                        'deviceUsername': self.get_error_msg(Error.DEVICE_USERNAME_DUPLICATE)[:-4]
                    }
        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _validate_gateway(self, rows_uplink_system, rows_gateway):
        """
        Validate if gateway's name is exist
        :param rows_gateway: dict {row_id: deviceName}
        """
        rows_error_msg = {}
        for row, name in list(rows_gateway.items()):
            if row in self.errors_rows_number:
                del rows_gateway[row]
                continue

        if rows_gateway.values():
            gateway_values = [
                gateway for gateway in rows_gateway.values() if gateway
            ]
            devices_name = ','.join(gateway_values)
            query = await postgres.fetch_many(
                query_gateway_sql.format(
                    devices_name=devices_name, tenantID=self.tenant_uid))
            query_gateway = dict(query)
            for row, name in rows_gateway.items():
                if rows_uplink_system[row] == 1 and name:
                    rows_error_msg[row] = {
                        'gateway': self.get_error_msg(Error.GATEWAY_NOT_REQUIRED)
                    }
                if rows_uplink_system[row] == 2 and not name:
                    rows_error_msg[row] = {
                        'gateway': self.get_error_msg(Error.GATEWAY_REQUIRED)
                    }
                if rows_uplink_system[row] == 2 and name and not query_gateway.get(name):
                    rows_error_msg[row] = {
                        'gateway': self.get_error_msg(Error.GATEWAY_NOT_EXIST) % name
                    }
            self.device_name_id = query_gateway
        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _validate_device_imei(self, rows_product, rows_devices_imei):
        """
        Validate if IMEI is valid and unique
        :param rows_product: dict {row_id: productName}
        :param rows_devices_imei: dict {row_id: IMEI}
        """

        rows_error_msg = {}
        devices_imei = []
        for row, value in list(rows_devices_imei.items()):
            if row in self.errors_rows_number:
                del rows_devices_imei[row]
                continue
            if self.product_name_protocol[rows_product[row]] == 3 and value is None:
                rows_error_msg[row] = {
                    'IMEI': self.get_error_msg(Error.IMEI_REQUIRED)
                }
                continue
            elif value is None:
                continue
            elif value in devices_imei:
                rows_error_msg[row] = {
                    'IMEI':
                        self.get_error_msg(Error.IMEI_DUPLICATE) %
                        rows_devices_imei.pop(row)
                }
            else:
                devices_imei.append(value)

        if devices_imei:
            devices_imei = ','.join(devices_imei)
            query = await postgres.fetch_many(
                query_device_by_imei_sql.format(
                    devices_imei=devices_imei, tenantID=self.tenant_uid))
            query_imeis = [i[0] for i in query]
            for row, imei in rows_devices_imei.items():
                if imei in query_imeis:
                    rows_error_msg[row] = {
                        'IMEI': self.get_error_msg(Error.IMEI_EXIST) % imei
                    }
        self.rows_errors_msg.update(rows_error_msg)
        self.errors_rows_number.extend(rows_error_msg.keys())

    async def _update_task_status(self,
                                  status: int,
                                  progress: float,
                                  import_status: ImportStatus,
                                  result=None):
        if result is None:
            result = {}
        message = STATUS_MESSAGE.get(import_status)
        code = import_status.value
        self.task_result['status'] = status
        self.task_result['progress'] = progress
        self.task_result['code'] = code
        self.task_result['message'] = message
        self.task_result['result'] = result
        # Update database once the status is 2(pending)
        if status == 2:
            result['message'] = message
            result['code'] = code
            update_dict = {
                'updateAt': datetime.now(),
                'taskStatus': status,
                'taskProgress': progress,
                'taskResult': json.dumps(result),
                'taskID': self.task_id
            }
            await update_task(postgres=postgres, update_dict=update_dict)

    def get_error_msg(self, error: Error):
        return get_row_error_message(error, self.language)


async def execute_with_transaction(sql: str) -> bool:
    """
    Execute sql with transaction
    :param sql: execute sql
    :return: True if execute successfully else False
    """
    execute_sql = f"BEGIN;" \
        f"{sql}" \
        f"COMMIT;"
    return await postgres.execute(execute_sql)
