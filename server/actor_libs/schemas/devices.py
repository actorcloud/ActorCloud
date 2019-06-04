from marshmallow import fields
from marshmallow.validate import OneOf

from actor_libs.schemas.fields import (
    EmqFloat, EmqInteger, EmqList,
    EmqString, EmqDateTime, EmqJson
)


__all__ = ['BaseDeviceSchema']


class DeviceScopeSchema:
    scope = EmqList(required=True)


class BaseDeviceSchema:
    deviceName = EmqString(required=True)
    deviceType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 1:endDevice. 2:gateway
    productID = EmqString(required=True, len_max=6)
    authType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 1:token 2:cert
    carrier = EmqInteger()
    upLinkNetwork = EmqInteger(allow_none=True, validate=OneOf(range(1, 8)))
    deviceID = EmqString(allow_none=True, len_min=8, len_max=36)
    deviceUsername = EmqString(allow_none=True, len_min=8, len_max=36)
    token = EmqString(allow_none=True, len_min=8, len_max=36)
    location = EmqString(allow_none=True)
    latitude = EmqFloat(allow_none=True)
    longitude = EmqFloat(allow_none=True)
    blocked = EmqInteger(allow_none=True)
    manufacturer = EmqString(allow_none=True)
    serialNumber = EmqString(allow_none=True)
    softVersion = EmqString(allow_none=True)
    hardwareVersion = EmqString(allow_none=True)
    deviceConsoleIP = EmqString(allow_none=True)
    deviceConsoleUsername = EmqString(allow_none=True)
    deviceConsolePort = EmqInteger(allow_none=True)
    mac = EmqString(allow_none=True)
    metaData = EmqJson(allow_none=True)
    description = EmqString(allow_none=True, len_max=300)
    deviceStatus = EmqInteger(dump_only=True)
    lastConnection = EmqDateTime(dump_only=True)
    groups = EmqList(allow_none=True, list_type=str, load_only=True)
    certs = EmqList(allow_none=True, list_type=int, load_only=True)
    productType = EmqInteger(load_only=True)  # 1:endDevice product 2:gateway product
    scopes = fields.Nested(DeviceScopeSchema, only='scope', many=True, dump_only=True)

    def __init__(self, *args, **kwargs):
        pass
