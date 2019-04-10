from enum import Enum, unique


__all__ = [
    'ImportStatus', 'STATUS_MESSAGE', 'get_row_error_message', 'Error', 'IMPORT_RENAME',
    'EXPORT_RENAME'
]


@unique
class ImportStatus(Enum):
    UPLOADED = 4001
    READING = 4002
    VALIDATING = 4003
    IMPORTING = 4004
    COMPLETED = 4005
    TEMPLATE_ERROR = 4006
    ABNORMAL = 4007
    LIMITED = 4008
    FAILED = 4009


STATUS_MESSAGE = {
    ImportStatus.UPLOADED: 'File upload completed',
    ImportStatus.READING: 'Reading file content',
    ImportStatus.VALIDATING: 'Validating data',
    ImportStatus.IMPORTING: 'Importing data',
    ImportStatus.COMPLETED: 'Import completed',
    ImportStatus.TEMPLATE_ERROR: 'Please follow the template to fill in the import data',
    ImportStatus.ABNORMAL: 'Abnormal data detected,import stop',
    ImportStatus.LIMITED: 'The number of imported devices exceeds the limit of devices',
    ImportStatus.FAILED: 'Data import failed, please check the data or try again later',
}


class Error(Enum):
    FORMAT_ERROR = 5001
    DEVICE_NAME_DUPLICATE = 5002
    DEVICE_ID_DUPLICATE = 5003
    DEVICE_ID_EXIST = 5004
    DEVICE_USERNAME_DUPLICATE = 5005
    PRODUCT_NOT_EXIST = 5006
    INDEX_REQUIRED = 5007
    INDEX_NOT_REQUIRED = 5008
    INDEX_INVALID = 5009
    GATEWAY_NOT_REQUIRED = 5010
    GATEWAY_REQUIRED = 5011
    GATEWAY_NOT_EXIST = 5012
    IMEI_REQUIRED = 5013
    IMEI_DUPLICATE = 5014
    IMEI_EXIST = 5015


ROW_ERROR_MESSAGE_ZH = {
    Error.FORMAT_ERROR: '格式错误, 请按填写说明填写',
    Error.DEVICE_NAME_DUPLICATE: '设备名重复(%s)',
    Error.DEVICE_ID_DUPLICATE: '设备编号重复(%s)',
    Error.DEVICE_ID_EXIST: '设备编号已存在(%s)',
    Error.DEVICE_USERNAME_DUPLICATE: '设备用户名重复(%s)',
    Error.PRODUCT_NOT_EXIST: '产品不存在(%s)',
    Error.INDEX_REQUIRED: 'Modbus协议产品必须填写索引',
    Error.INDEX_NOT_REQUIRED: '非Modbus协议产品不填写索引(%d)',
    Error.INDEX_INVALID: '索引必须是0~255之间的数字(%d)',
    Error.GATEWAY_NOT_REQUIRED: '所属网关不填写(上联系统为云时，不填)',
    Error.GATEWAY_REQUIRED: '所属网关未填写(上联系统为网关时，必填)',
    Error.GATEWAY_NOT_EXIST: '所属网关不存在(%s)',
    Error.IMEI_REQUIRED: 'LwM2M协议产品必须填写IMEI',
    Error.IMEI_DUPLICATE: 'IMEI已存在(%s)',
    Error.IMEI_EXIST: 'IMEI重复(%s)',
}

ROW_ERROR_MESSAGE_EN = {
    Error.FORMAT_ERROR: 'Format error',
    Error.DEVICE_NAME_DUPLICATE: 'Device name duplicate(%s)',
    Error.DEVICE_ID_DUPLICATE: 'Device id duplicate(%s)',
    Error.DEVICE_ID_EXIST: 'Device id already exists(%s)',
    Error.DEVICE_USERNAME_DUPLICATE: 'Device username duplicate(%s)',
    Error.PRODUCT_NOT_EXIST: 'Product does not exist(%s)',
    Error.INDEX_REQUIRED: 'Modbus index is required for Modbus protocol',
    Error.INDEX_NOT_REQUIRED: 'Modbus index is not required for non-Modbus protocol(%d)',
    Error.INDEX_INVALID: 'The index must be a number between 0 and 255(%d)',
    Error.GATEWAY_NOT_REQUIRED: 'Gateway is not required',
    Error.GATEWAY_REQUIRED: 'Gateway is required',
    Error.GATEWAY_NOT_EXIST: 'Gateway does not exist(%s)',
    Error.IMEI_REQUIRED: 'IMEI is required for LwM2M protocol',
    Error.IMEI_DUPLICATE: 'IMEI already exist(%s)',
    Error.IMEI_EXIST: 'IMEI duplicate(%s)',
}


def get_row_error_message(error: Error, language: str):
    message = ''
    if language == 'en':
        message = ROW_ERROR_MESSAGE_EN.get(error)
    elif language == 'zh':
        message = ROW_ERROR_MESSAGE_ZH.get(error)
    return message


IMPORT_RENAME = {
    '设备名称': 'deviceName',
    '所属产品': 'product',
    '设备类型': 'deviceType',
    '认证类型': 'authType',
    '上联系统': 'upLinkSystem',
    '设备编号': 'deviceID',
    '设备用户名': 'deviceUsername',
    '设备秘钥': 'token',
    '经度': 'longitude',
    '纬度': 'latitude',
    '安装位置': 'location',
    '序列号': 'serialNumber',
    '软件版本': 'softVersion',
    '硬件版本': 'hardwareVersion',
    '制造商': 'manufacturer',
    '描述': 'description',
    '所属网关': 'gateway',
    '索引': 'modBusIndex',
    '自动订阅': 'autoSub',
    'IMEI': 'IMEI'
}

EXPORT_RENAME = {
    'deviceName': '设备名称',
    'deviceType': '设备类型',
    'authType': '认证类型',
    'product': '所属产品',
    'upLinkSystem': '上联系统',
    'modBusIndex': '索引',
    'gateway': '所属网关',
    'deviceID': '设备编号',
    'deviceUsername': '设备用户名',
    'token': '设备秘钥',
    'longitude': '经度',
    'latitude': '纬度',
    'location': '安装位置',
    'softVersion': '软件版本',
    'hardwareVersion': '硬件版本',
    'manufacturer': '制造商',
    'serialNumber': '序列号',
    'description': '描述',
    'autoSub': '自动订阅'
}
