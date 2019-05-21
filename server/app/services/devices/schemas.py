import os
import re
from typing import List

from flask import g, request, current_app
from marshmallow import (
    fields, post_dump, post_load, pre_load,
    validates, validates_schema, validate
)
from marshmallow.validate import OneOf
from sqlalchemy import func

from actor_libs.cache import Cache
from actor_libs.database.orm import db
from actor_libs.errors import (
    DataExisted, DataNotFound, FormInvalid, ResourceLimited
)
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDict, EmqFloat, EmqInteger, EmqList,
    EmqString, EmqDateTime, EmqJson
)
from actor_libs.utils import generate_uuid
from app.models import (
    Device, EndDevice, Gateway, Product,
    Group, GroupDevice, Cert, CertDevice, Channel
)


__all__ = [
    'DeviceSchema', 'EndDeviceSchema', 'GatewaySchema',
    'GroupSchema', 'GroupDeviceSchema', 'CertSchema', 'CertDeviceSchema',
    'DeviceLocationSchema', 'DeviceScopeSchema', 'ChannelSchema',
    'Lwm2mItemSchema', 'Lwm2mObjectSchema'
]


class DeviceScopeSchema(BaseSchema):
    scope = EmqList(required=True)


class DeviceSchema(BaseSchema):
    deviceName = EmqString(required=True)
    deviceType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 1:endDevice. 2:gateway
    productID = EmqString(required=True, len_max=6)
    authType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 1:token 2:cert
    upLinkNetwork = EmqInteger(required=True, validate=OneOf(range(1, 8)))
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

    @validates('deviceType')
    def device_name_is_exist(self, value):
        device_type = self.get_origin_obj('deviceType')
        if device_type and device_type != value:
            # deviceType not support update
            raise FormInvalid(field='deviceType')
        product_type = self.get_request_data('productType')
        if device_type != product_type:
            raise FormInvalid(field='deviceType')

    @validates_schema
    def device_uid_is_exist(self, data):
        device_uid = data.get('deviceID')
        username = data.get('deviceUsername')

        if self.get_origin_obj('deviceID'):
            return data
        if not device_uid or not username:
            device_uuid = generate_uuid()
            data['deviceID'] = device_uuid
            data['deviceUsername'] = device_uuid
            return data
        # unique within the tenant
        device_uid = db.session.query(Device.deviceID) \
            .filter(Device.deviceID == device_uid,
                    Device.tenantID == g.tenant_uid).first()
        if device_uid:
            raise DataExisted(field='deviceID')
        # unique within the platform
        device = db.session.query(Device.id) \
            .filter(Device.deviceID == device_uid,
                    Device.deviceUsername == username).first()
        if device:
            raise FormInvalid(field='deviceID')
        return data

    @pre_load
    def handle_origin_data(self, data):
        product_uid = data.get('productID')
        if not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        product = Product.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.productID == product_uid).first()
        if not product:
            raise DataNotFound(field='productID')
        data['productType'] = product.productType
        data['productID'] = product.productID
        data['cloudProtocol'] = product.cloudProtocol
        data['gatewayProtocol'] = product.gatewayProtocol
        return data

    @post_load
    def handle_validated_data(self, data):
        data = self.handle_put_request(data)
        groups_uid: List[str] = data.get('groups')
        if groups_uid:
            groups = Group.query \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(Group.groupID.in_(set(groups_uid))) \
                .many(expect_result=len(groups_uid))
            data['groups'] = groups
        if data['authType'] == 2:
            certs_id: List[int] = data.get('certs')
            if not certs_id:
                raise FormInvalid(field='certs')
            certs = Cert.query \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(Cert.id.in_(set(certs_id))) \
                .many(expect_result=len(certs_id))
            data['certs'] = certs
        return data

    def handle_put_request(self, data):
        """ Device update not support deviceID, deviceUsername, token """

        if request.method != 'PUT':
            return data
        data['deviceID'] = self.get_origin_obj('deviceID')
        data['deviceUsername'] = self.get_origin_obj('deviceUsername')
        data['token'] = self.get_origin_obj('token')
        if data.get('lwm2m'):
            data['lwm2m']['IMEI'] = self.get_origin_obj('deviceID')
        return data

    @post_dump
    def handle_dump_data(self, data):
        device_id = data['id']
        device_certs = Cert.query \
            .join(CertDevice, CertDevice.c.certIntID == Cert.id) \
            .filter(CertDevice.c.deviceIntID == device_id).all()
        device_groups = Group.query \
            .join(GroupDevice, GroupDevice.c.groupID == Group.groupID) \
            .filter(GroupDevice.c.deviceIntID == device_id).all()
        groups = []
        group_index = []
        for group in device_groups:
            groups.append(group.groupID)
            group_index.append({'value': group.id, 'label': group.groupName})
        data['groups'] = groups
        data['groupsIndex'] = group_index
        if data['authType'] == 2:
            # cert auth
            certs = []
            cert_index = []
            for cert in device_certs:
                certs.append(cert.id)
                cert_index.append({'value': cert.id, 'label': cert.certName})
            data['certs'] = certs
            data['certsIndex'] = cert_index
        return data


class EndDeviceSchema(DeviceSchema):
    loraData = EmqDict(allow_none=True)  # lora  data extend
    modbusData = EmqDict(allow_none=True)  # modbus  data extend
    lwm2mData = EmqDict(allow_none=True)  # lwm2m data extend
    upLinkSystem = EmqInteger(required=True)  # 1:cloud 2:device 3:gateway
    parentDevice = EmqInteger(allow_none=True)
    gateway = EmqInteger(allow_none=True)
    cloudProtocol = EmqInteger(load_only=True)

    @validates('deviceName')
    def device_name_is_exist(self, value):
        if self._validate_obj('deviceName', value):
            return

        device_name = EndDevice.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(EndDevice.deviceName == value) \
            .with_entities(EndDevice.deviceName).first()
        if device_name:
            raise DataExisted(field='deviceName')

    @validates_schema
    def validate_uplink_system(self, data):
        uplink_system = data.get('upLinkSystem')
        if uplink_system == 1:
            data['parentDevice'], data['gateway'] = None, None
        elif uplink_system == 2 and isinstance(data.get('parentDevice'), int):
            parent_device = data['parentDevice']
            end_device_id = EndDevice.query \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(EndDevice.id == parent_device) \
                .with_entities(EndDevice.id).first()
            if not end_device_id:
                raise DataNotFound(field='parentDevice')
            data['parentDevice'], data['gateway'] = end_device_id, None
        elif uplink_system == 3 and isinstance(data.get('gateway'), int):
            gateway = data['gateway']
            gateway_id = Gateway.query \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(Gateway.id == gateway) \
                .with_entities(Gateway.id).first()
            if not gateway_id:
                raise DataNotFound(field='gateway')
            data['parentDevice'], data['gateway'] = None, gateway_id
        else:
            raise FormInvalid(field='upLinkSystem')
        return data

    @validates_schema
    def validate_cloud_protocol(self, data):
        cloud_protocol = data.get('cloudProtocol')
        if cloud_protocol in [1, 2, 5, 6]:
            # mqtt, coap, http, websocket
            data['loraData'], data['lwm2mData'], data['modbusData'] = None, None, None
        elif cloud_protocol == 3 and data.get('lwm2mData'):
            # lwm2m data
            data['loraData'], data['modbusData'] = None, None
            data['lwm2mData'] = Lwm2mDeviceSchema().load(data['lwm2mData']).data
            data['deviceID'] = data['lwm2mData']['IMEI']
        elif cloud_protocol == 4 and data.get('loraData'):
            # lora data
            data['lwm2mData'], data['modbusData'] = None, None

            data['loraData'] = LoRaDeviceSchema().load(data['loraData']).data
        elif cloud_protocol == 7 and data.get('modbusData'):
            # modbus
            data['lwm2mData'], data['loraData'] = None, None
            data['modbusData'] = ModbusDeviceSchema().load(data['modbusData']).data
        else:
            error_fields = {3: 'lwm2mData', 4: 'loraData', 5: 'modbusData'}
            raise FormInvalid(field=error_fields.get(cloud_protocol, 'cloudProtocol'))
        return data

    @post_dump
    def handle_uplink_system(self, data):
        if data['upLinkSystem'] == 2:
            parentDevice = data['parentDevice']
            parent_device = Device.query.filter(Device.id == parentDevice) \
                .with_entities(Device.deviceName).first()
            data['parentDeviceName'] = parent_device.deviceName
        elif data['upLinkSystem'] == 3:
            gateway = data['gateway']
            gateway = Device.query.filter(Device.id == gateway) \
                .with_entities(Device.deviceName).first()
            data['gatewayName'] = gateway.deviceName
        return data


class GatewaySchema(DeviceSchema):
    gatewayProtocol = EmqInteger(load_only=True)

    @validates('deviceName')
    def device_name_is_exist(self, value):
        if self._validate_obj('deviceName', value):
            return

        device_name = Gateway.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Gateway.deviceName == value) \
            .with_entities(Gateway.deviceName).first()
        if device_name:
            raise DataExisted(field='deviceName')


class GroupSchema(BaseSchema):
    groupID = EmqString(dump_only=True)
    groupName = EmqString(required=True)
    description = EmqString(allow_none=True, len_max=300)

    @validates('groupName')
    def group_name_is_exist(self, value):
        if self._validate_obj('groupName', value):
            return

        query = db.session.query(Group.groupName) \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Group.groupName == value).first()
        if query:
            raise DataExisted(field='groupName')


class GroupDeviceSchema(BaseSchema):
    devices = EmqList(required=True, list_type=int)

    @post_load
    def handle_loads(self, data):
        group_id = request.view_args.get('group_id')
        devices_id = data['devices']
        group_devices_id = db.session.query(GroupDevice.c.deviceIntID) \
            .join(Group, Group.groupID == GroupDevice.c.groupID) \
            .filter(Group.id == group_id).all()
        add_devices_id = set(devices_id).difference(set(group_devices_id))
        if len(group_devices_id) + len(add_devices_id) > 1001:
            raise ResourceLimited(field='devices')
        devices = Device.query.filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Device.id.in_(add_devices_id)).all()
        if len(devices) != len(add_devices_id):
            raise DataNotFound(field='devices')
        data['devices'] = devices
        return data


class CertSchema(BaseSchema):
    certName = EmqString(required=True)
    enable = EmqInteger(allow_none=True)
    CN = EmqString(dump_only=True)
    key = EmqString(dump_only=True)
    cert = EmqString(dump_only=True)
    root = EmqString(dump_only=True)

    @validates('certName')
    def name_is_exist(self, value):
        if self._validate_obj('certName', value):
            return
        query = db.session.query(Cert.certName) \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Cert.certName == value).first()
        if query:
            raise DataExisted(field='certName')

    @post_dump
    def dump_root(self, data):
        certs_path = current_app.config.get('CERTS_PATH')
        root_ca_path = os.path.join(certs_path, 'actorcloud/root_ca.crt')
        with open(root_ca_path, 'r') as root_crt_file:
            st_root_cert = root_crt_file.read()
        data['root'] = st_root_cert
        return data


class CertDeviceSchema(BaseSchema):
    devices = EmqList(required=True, list_type=int)

    @post_load
    def handle_cert_devices(self, data):
        devices_id = data['devices']
        devices = Device.query \
            .filter(Device.id.in_(set(devices_id)), Device.authType == 2) \
            .many(allow_none=False, expect_result=len(devices_id))
        cert_id = self.get_origin_obj('id')
        exist_cert_devices = db.session \
            .query(func.count(CertDevice.c.deviceIntID)) \
            .filter(CertDevice.c.certIntID == cert_id,
                    CertDevice.c.deviceIntID.in_(set(devices_id))) \
            .scalar()
        if exist_cert_devices:
            raise DataExisted(field='devices')
        data['devices'] = devices
        return data


class DeviceLocationSchema(BaseSchema):
    longitude = EmqFloat(allow_none=True)
    latitude = EmqFloat(allow_none=True)
    location = EmqString(allow_none=True, len_max=300)


class Lwm2mObjectSchema(BaseSchema):
    objectName = EmqString(required=True)
    objectID = EmqInteger(required=True)
    description = EmqString()
    objectURN = EmqString()
    objectVersion = EmqString()
    multipleInstance = EmqString(required=True)
    mandatory = EmqString()  # mandatory: Optional，Mandatory


class Lwm2mItemSchema(BaseSchema):
    itemName = EmqString(required=True)
    itemID = EmqInteger(required=True)
    description = EmqString()
    itemType = EmqString(required=True)
    itemOperations = EmqString(required=True)  # R/W/RW/E
    itemUnit = EmqString(required=True)
    rangeEnumeration = EmqString()
    mandatory = EmqString()  # mandatory: Optional，Mandatory
    multipleInstance = EmqString(required=True)
    objectID = EmqInteger(required=True)


# device protocol validate schema
class Lwm2mDeviceSchema(BaseSchema):
    is_private = True
    autoSub = EmqInteger(required=True, validate=OneOf([0, 1]))
    IMEI = EmqString(required=True, len_max=15)
    IMSI = EmqString(required=True, len_max=15)


class ModbusDeviceSchema(BaseSchema):
    is_private = True
    modBusIndex = EmqInteger(required=True)  # modbus index

    @validates('modBusIndex')
    def validate_modbus_index(self, value):
        if value < 0 or value > 256:
            raise FormInvalid(field='modBusIndex')


class LoRaDeviceSchema(BaseSchema):
    is_private = True
    type = EmqString(required=True, validate=lambda x: x in ['otaa', 'abp'])
    region = EmqString(allow_none=True)
    fcntCheck = EmqInteger(allow_none=True)
    ottaInfo = EmqDict(load_only=True)  # lora otta type info
    abpInfo = EmqDict(load_only=True)  # lora abp type info

    @validates('fcntCheck')
    def validate_fcnt_check(self, value):
        if value is None:
            return
        cache = Cache()
        dict_code_cache = cache.dict_code
        fcnt_check_cache = dict_code_cache['fcntCheck']
        if value not in fcnt_check_cache.keys():
            raise DataNotFound(field='fcntCheck')

    @pre_load
    def handle_origin_data(self, data):
        lora_type = data['type']
        if lora_type == 'otaa':
            data['ottaInfo'] = LoRaOTTASchema().load(data).data
        elif lora_type == 'abp':
            data['abpInfo'] = LoRaABPSchema().load(data).data
        return data

    @post_load
    def handle_validated_data(self, data):
        lora_type = data['type']
        if lora_type == 'otaa':
            otta_info = data.pop('ottaInfo')
            data.update(otta_info)
        elif lora_type == 'abp':
            abp_info = data.pop('abpInfo')
            data.update(abp_info)
        return data


class LoRaOTTASchema(BaseSchema):
    region = EmqString(required=True)
    appEUI = EmqString(required=True, validate=validate.Length(equal=16))
    appKey = EmqString(required=True, validate=validate.Length(equal=32))
    fcntCheck = EmqInteger(required=True)
    canJoin = EmqInteger(required=True)

    @validates('region')
    def validate_region(self, value):
        if value is None:
            return
        cache = Cache()
        dict_code_cache = cache.dict_code
        region_cache = dict_code_cache['region']
        if value not in region_cache.keys():
            raise DataNotFound(field='region')

    @post_dump
    def dump_can_join(self, data):
        # bool to 0/1
        data['canJoin'] = 1 if data.get('canJoin') else 0
        return data


class LoRaABPSchema(BaseSchema):
    region = EmqString(required=True)
    nwkSKey = EmqString(required=True, validate=validate.Length(equal=32))
    appSKey = EmqString(required=True, validate=validate.Length(equal=32))
    fcntUp = EmqInteger(required=True)
    fcntDown = EmqInteger(required=True)
    fcntCheck = EmqInteger(required=True)
