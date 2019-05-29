from typing import Dict, List

from marshmallow import Schema
from marshmallow.validate import OneOf

from actor_libs.database.async_db import db
from actor_libs.schemas.devices import BaseDeviceSchema
from actor_libs.schemas.fields import EmqInteger, EmqString
from .multi_language import Error, get_row_error_message
from .sql_statements import (
    query_devices_name_sql, query_product_sql, query_device_uid_sql,
    query_gateway_sql
)


class ImportDeviceSchema(Schema, BaseDeviceSchema):
    deviceType = EmqInteger(allow_none=True)
    productID = EmqString(allow_none=True, len_max=6)
    # devices import
    upLinkSystem = EmqInteger(required=True, validate=OneOf([1, 3]))  # 1:cloud, 3:gateway
    product = EmqString(required=True)  # product name
    gateway = EmqString(allow_none=True)  # gateway name


async def validates_schema(import_records, request_json):
    """
    schema to validate imported data
    :param import_records:
    :param request_json:
    """
    validated_schema = ImportDeviceSchema(many=True).load(import_records)
    validated_records = validated_schema.data
    validated_errors = validated_schema.errors
    for row, info in validated_errors.items():
        for column, _ in info.items():
            error_msg = get_row_error_message(
                Error.FORMAT_ERROR, request_json['language']
            )
            validated_errors[row][column] = error_msg
    rows_error_msg: Dict = validated_errors
    rows_error_msg, devices_attr_info = await _validate_import_device_info(
        validated_records, rows_error_msg, request_json
    )
    return rows_error_msg, devices_attr_info


async def _validate_import_device_info(validated_records: List[Dict],
                                       rows_error_msg: Dict,
                                       request_json: Dict):
    tenant_uid = request_json['tenantID']
    language = request_json['language']
    # validate data for each row
    rows_device_name = {}  # validate deviceNam e(unique of tenant)
    rows_product = {}  # validate product(exist product of tenant)
    rows_device_uid = {}  # validate deviceID(unique of platform)
    rows_gateway = {}  # 校验网关(是否存在 租户)
    for row, record in enumerate(validated_records):
        if rows_error_msg.get(row):
            continue
        rows_device_name[row] = record.get('deviceName')
        rows_product[row] = record.get('product')
        if record.get('upLinkSystem') == 3 and record.get('gateway'):
            rows_gateway[row] = record.get('gateway')
        if record.get('deviceID'):
            rows_device_uid[row] = record.get('deviceID')
    errors_device_name = await _validate_devices_name(
        rows_device_name, language, tenant_uid
    )
    rows_error_msg.update(errors_device_name)
    errors_product, products_info = await _validate_products(
        rows_product, language, tenant_uid
    )
    rows_error_msg.update(errors_product)
    errors_device_uid = await _validate_devices_uid(
        rows_device_uid, language
    )
    rows_error_msg.update(errors_device_uid)
    errors_gateway, gateways_info = await _validate_gateway(
        rows_gateway, language, tenant_uid
    )
    rows_error_msg.update(errors_gateway)
    devices_attr_info = {
        'products_info': products_info,
        'gateways_info': gateways_info
    }
    return rows_error_msg, devices_attr_info


async def _validate_devices_name(rows_device_name, language, tenant_uid):
    """
    Validate device name is unique
    :param device_name: dict {row_id: deviceName}
    """
    rows_error_msg = {}
    validate_names = []
    for row, device_name in rows_device_name.items():
        if device_name in validate_names:
            error_msg: str = get_row_error_message(
                Error.DEVICE_NAME_DUPLICATE, language
            )
            rows_error_msg[row] = {
                'deviceName': error_msg % device_name
            }
        else:
            validate_names.append(device_name)

    if validate_names:
        devices_name = ','.join(set(validate_names))
        query_sql = query_devices_name_sql.format(
            devicesName=devices_name, tenantID=tenant_uid
        )
        query_result = await db.fetch_many(query_sql)
        if not query_result:
            # no identical device name
            return rows_error_msg
        query_names = [i[0] for i in query_result]
        for row, device_name in rows_device_name.items():
            if rows_error_msg.get(row):
                continue
            if device_name in query_names:
                error_msg: str = get_row_error_message(
                    Error.DEVICE_NAME_DUPLICATE, language
                )
                rows_error_msg[row] = {
                    'deviceName': error_msg % device_name
                }
    return rows_error_msg


async def _validate_products(rows_product, language, tenant_uid):
    """
    Validate if product is exist
    :param rows_product: dict {row_id: productName}
    """

    rows_error_msg = {}
    products_info = {}
    products_name = ','.join(set(rows_product.values()))
    query_sql = query_product_sql.format(
        productsName=products_name, tenantID=tenant_uid
    )
    query_result = await db.fetch_many(query_sql)
    # collect devices product info
    for record in query_result:
        products_info[record['productName']] = {
            'productID': record['productID'],
            'cloudProtocol': record['cloudProtocol']
        }
    # validate product does it exist
    for row, name in rows_product.items():
        if not products_info.get(name):
            error_msg: str = get_row_error_message(
                Error.PRODUCT_NOT_EXIST, language
            )
            rows_error_msg[row] = {
                'product': error_msg % name
            }
    return rows_error_msg, products_info


async def _validate_devices_uid(rows_device_uid, language):
    """
    Validate deviceID is unique in all platforms
    :param rows_device_uid: dict {row_id: deviceID}
    """

    rows_error_msg = {}
    validate_devices_uid = []
    for row, device_uid in rows_device_uid.items():
        if device_uid in validate_devices_uid:
            error_msg: str = get_row_error_message(
                Error.DEVICE_ID_DUPLICATE, language
            )
            rows_error_msg[row] = {
                'deviceID': error_msg % device_uid
            }
        else:
            validate_devices_uid.append(device_uid)

    if validate_devices_uid:
        devices_uid = ','.join(set(validate_devices_uid))
        query_sql = query_device_uid_sql.format(devicesID=devices_uid)
        query_result = await db.fetch_many(query_sql)
        query_devices_uid = [i[0] for i in query_result]
        for row, device_uid in rows_device_uid.items():
            if rows_error_msg.get(row):
                continue
            if device_uid in query_devices_uid:
                error_msg: str = get_row_error_message(
                    Error.DEVICE_ID_DUPLICATE, language
                )
                rows_error_msg[row] = {
                    'deviceID': error_msg % device_uid
                }
    return rows_error_msg


async def _validate_gateway(rows_gateway, language, tenant_uid):
    """
    Validate if gateway's name is exist
    :param rows_gateway: dict {row_id: deviceName}
    """
    rows_error_msg = {}
    if not rows_gateway:
        return rows_error_msg, {}
    gateways_name = ','.join(set(rows_gateway.values()))
    query_sql = query_gateway_sql.format(
        gatewaysName=gateways_name,
        tenantID=tenant_uid
    )
    query_result = await db.fetch_many(query_sql)
    gateways_info = dict(query_result)
    for row, gateway_name in rows_gateway.items():
        if not gateways_info.get(gateway_name):
            error_msg: str = get_row_error_message(
                Error.GATEWAY_NOT_EXIST, language
            )
            rows_error_msg[row] = {
                'gateway': error_msg % gateway_name
            }
    return rows_error_msg, gateways_info
