import json
import os
import re
from typing import AnyStr

from flask import g, request, current_app
from marshmallow import (
    fields, post_dump, post_load, pre_load, validates, validates_schema, validate
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
    EmqDict, EmqFloat, EmqInteger, EmqList, EmqString, EmqDateTime
)
from actor_libs.utils import generate_uuid
from app.models import (
    Cert, Client, Device, Gateway, Group, Tenant,
    Product, User, GroupClient, CertClient
)


__all__ = [
    'ClientSchema', 'DeviceSchema', 'DeviceUpdateSchema', 'DeviceScopeSchema', 'GatewaySchema',
    'GatewayUpdateSchema', 'GroupSchema', 'GroupDeviceSchema', 'CertSchema', 'CertClientSchema',
    'DeviceLocationSchema', 'AddDeviceSchema', 'DeviceIdsSchema',
    'Lwm2mObjectSchema', 'Lwm2mItemSchema',
    'ChannelSchema', 'ChannelComSchema', 'ChannelTcpSchema',
]


class DeviceScopeSchema(BaseSchema):
    scope = EmqList(required=True)


class ClientSchema(BaseSchema):
    deviceName = EmqString(required=True)
    productID = EmqString(requied=True, len_max=6)
    authType = EmqInteger(allow_none=True, validate=OneOf([1, 2]))  # 1:token 2:cert
    deviceID = EmqString(allow_none=True, len_min=8, len_max=36)
    deviceUsername = EmqString(allow_none=True, len_min=8, len_max=36)
    token = EmqString(allow_none=True, len_min=8, len_max=36)
    location = EmqString(allow_none=True)
    latitude = EmqFloat(allow_none=True)
    longitude = EmqFloat(allow_none=True)
    blocked = EmqInteger(allow_none=True)
    cloudProtocol = EmqInteger(allow_none=True)
    manufacturer = EmqString(allow_none=True)
    serialNumber = EmqString(allow_none=True)
    softVersion = EmqString(allow_none=True)
    hardwareVersion = EmqString(allow_none=True)
    deviceConsoleIP = EmqString(allow_none=True)
    deviceConsoleUsername = EmqString(allow_none=True)
    deviceConsolePort = EmqInteger(allow_none=True)
    description = EmqString(allow_none=True, len_max=300)
    deviceStatus = EmqInteger(dump_only=True)
    clientType = EmqInteger(dump_only=True)
    lastConnection = EmqDateTime(dump_only=True)
    userIntID = EmqInteger(dump_only=True)
    tenantID = EmqString(dump_only=True)
    groups = EmqList(allow_none=True, list_type=str, load_only=True)
    certs = EmqList(allow_none=True, list_type=str, load_only=True)

    @validates_schema
    def device_uid_is_exist(self, in_data):
        """
        deviceID unique within the tenant,deviceID and username unique within the platform
        lora device no need to validate temporarily
        Do not allow to update deviceID, username, token except lora
        """

        device_id = in_data.get('deviceID')
        username = in_data.get('deviceUsername')
        if not device_id or not username:
            return

        # unique within the tenant
        device_uid = db.session.query(Client.deviceID) \
            .filter(Client.deviceID == device_id,
                    Client.tenantID == g.tenant_uid).first()
        if device_uid:
            raise DataExisted(field='deviceID')
        # unique within the platform
        device = db.session \
            .query(Client.id) \
            .filter(Client.deviceID == device_id,
                    Client.deviceUsername == username).first()
        if device:
            raise FormInvalid(field='deviceID')

    @staticmethod
    def validate_create_permission(product_uid: AnyStr):
        if request.method != 'POST':
            return
        # Check if it needs to validate device count
        tenant_devices = db.session.query(Tenant.deviceCount) \
            .filter(Tenant.tenantID == g.tenant_uid).scalar()
        if tenant_devices > 0:
            device_count = db.session.query(func.count(Client.id)) \
                .filter(Client.tenantID == g.tenant_uid).scalar()
            if device_count >= tenant_devices:
                raise ResourceLimited(field='deviceCount')

    @staticmethod
    def convert_groups_object(in_data):
        groups_uid = in_data.get('groups')
        if not groups_uid:
            return in_data
        if not isinstance(groups_uid, list):
            raise FormInvalid(field='groups')
        groups = Group.query.filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Group.groupID.in_(set(groups_uid))).all()
        if len(groups) != len(groups_uid):
            raise DataNotFound(field='groups')
        in_data['groups'] = groups
        return in_data

    @staticmethod
    def convert_certs_object(in_data):
        certs_id = in_data.get('certs')
        if not certs_id:
            return in_data
        if not isinstance(certs_id, list):
            raise FormInvalid(field='certs')
        certs = Cert.query.filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Cert.id.in_(set(certs_id))).all()
        if len(certs) != len(certs_id):
            raise DataNotFound(field='certs')
        in_data['certs'] = certs
        return in_data

    @post_load
    def handle_post_load(self, in_data):
        """ Generate deviceID, deviceUsername if None"""

        in_data = self.convert_groups_object(in_data)
        in_data = self.convert_certs_object(in_data)
        if request.method != 'POST':
            return in_data
        device_uid = in_data.get('deviceID')
        if not device_uid:
            device_uid = generate_uuid()
            in_data['deviceID'] = device_uid
        if not in_data.get('deviceUsername'):
            in_data['deviceUsername'] = device_uid
        return in_data


class DeviceSchema(ClientSchema):
    upLinkSystem = EmqInteger(allow_none=True)  # 1:cloud 2:gateway 3:device
    lora = EmqDict(allow_none=True)  # lora config
    modBusIndex = EmqInteger(allow_none=True)  # modbus index
    metaData = EmqString(allow_none=True)
    parentDevice = EmqInteger(allow_none=True)
    gateway = EmqInteger(allow_none=True)
    IMEI = EmqString(allow_none=True, len_max=15)
    IMSI = EmqString(allow_none=True, len_max=15)
    carrier = EmqInteger(allow_none=True, validate=OneOf([1, 2, 3, 4]))
    physicalNetwork = EmqInteger(allow_none=True, validate=OneOf([1, 2, 3, 4, 5, 6]))
    autoSub = EmqInteger(allow_none=True, validate=OneOf([0, 1]))
    autoCreateCert = EmqInteger(allow_none=True, validate=OneOf([0, 1]))
    productIntID = EmqInteger(load_only=True)
    deviceStatus = EmqInteger(dump_only=True)
    scopes = fields.Nested(DeviceScopeSchema, only='scope', many=True, dump_only=True)

    @validates('deviceName')
    def device_name_is_exist(self, value):
        if self._validate_obj('deviceName', value):
            return
        query = db.session.query(Device.deviceName) \
            .filter(Device.deviceName == value,
                    Device.tenantID == g.tenant_uid) \
            .first()
        if query:
            raise DataExisted(field='deviceName')

    @validates('metaData')
    def validate_json(self, value):
        if not value:
            return
        try:
            json.loads(value)
        except Exception:
            raise FormInvalid(field='metaData')

    @validates_schema
    def validate_uplink_system(self, in_data):

        uplink_system = in_data.get('upLinkSystem')
        cloud_protocol = in_data.get('cloudProtocol')

        if cloud_protocol == 3:
            return in_data
        if uplink_system not in [1, 2, 3]:
            raise FormInvalid(field='upLinkSystem')
        if uplink_system == 2:
            # gateway
            if cloud_protocol == 4:
                return
            gateway_id = in_data.get('gateway')
            if not isinstance(gateway_id, int):
                raise FormInvalid(field='gateway')
            gateway = db.session.query(Gateway.id) \
                .filter(Gateway.id == gateway_id,
                        Gateway.tenantID == g.tenant_uid).first()
            if not gateway:
                raise DataNotFound(field='gateway')
        elif uplink_system == 3:
            # device
            device_id = in_data.get('parentDevice')
            if not isinstance(device_id, int):
                raise FormInvalid(field='parentDevice')
            device_id = db.session.query(Device.id) \
                .filter(Device.id == device_id,
                        Device.tenantID == g.tenant_uid) \
                .first()
            if not device_id:
                raise FormInvalid(field='parentDevice')
        return in_data

    @validates_schema
    def validate_cloud_protocol(self, in_data):
        """ Validate device by cloud protocol """

        if in_data.get('cloudProtocol'):
            cloud_protocol = in_data.get('cloudProtocol')
        else:
            cloud_protocol = self.get_origin_obj('cloudProtocol')
        if in_data.get('authType'):
            auth_type = in_data.get('authType')
        else:
            auth_type = self.get_origin_obj('authType')

        if cloud_protocol in (1, 2, 5, 6):
            # 1:mqtt, 2:lora, 5:http, 6:webSocket
            if not auth_type:
                raise FormInvalid(field='authType')
        elif cloud_protocol == 3:
            # 3:lwm2m
            if not auth_type:
                raise FormInvalid(field='authType')
            if in_data.get('autoSub') not in (0, 1):
                raise FormInvalid(field='autoSub')
            imei = in_data.get('IMEI')
            if self._validate_obj('IMEI', imei):
                return
            imei_query = db.session.query(Client.IMEI) \
                .filter(Client.IMEI == imei).first()
            if imei_query:
                raise DataExisted(field='IMEI')
        elif cloud_protocol == 4:
            # 4:lora
            if not isinstance(in_data.get('lora'), dict):
                raise FormInvalid(field='lora')
        elif cloud_protocol == 7:
            # 7:modbus
            modbus_index = in_data.get('modBusIndex')
            if modbus_index not in range(0, 256):
                raise FormInvalid(field='modBusIndex')

    @validates_schema
    def validate_modbus_index(self, in_data):

        uplink_system = in_data.get('upLinkSystem')
        cloud_protocol = in_data.get('cloudProtocol')
        gateway_protocol = in_data.get('gatewayProtocol')
        modbus_index = in_data.get('modBusIndex')
        if any([self._validate_obj('modBusIndex', modbus_index),
                uplink_system != 2, cloud_protocol != 7,
                gateway_protocol != 7]):
            return

        gateway_id = in_data.get('gateway')
        query = db.session.query(Device.modBusIndex) \
            .filter(Device.gateway == gateway_id,
                    Device.modBusIndex == modbus_index) \
            .first()
        if query:
            raise DataExisted(field='modBusIndex')

    @staticmethod
    def load_and_validate_lora(in_data):

        lora_data = in_data.get('lora')
        if not isinstance(lora_data, dict):
            raise FormInvalid(field='lora')
        lora_type = lora_data.get('type')
        if not isinstance(lora_type, str):
            raise FormInvalid(field='loraType')

        if lora_type == 'otaa':
            in_data['lora'] = LoRaOTTASchema().load(lora_data).data
        elif lora_type == 'abp':
            in_data['lora'] = LoRaABPSchema().load(lora_data).data
            # abp: gateway required
            if not in_data.get('gateway'):
                raise FormInvalid(field='gateway')
        else:
            raise FormInvalid(field='loraType')
        return in_data

    @pre_load
    def handle_pre_load(self, in_data):

        uplink_system = in_data.get('upLinkSystem')
        product_uid = in_data.get('productID')
        if not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        self.validate_create_permission(product_uid)
        if uplink_system != 2:
            in_data['gateway'] = None
        elif uplink_system != 3:
            in_data['parentDevice'] = None

        product = db.session.query(Product.cloudProtocol, Product.id) \
            .join(User, User.id == Product.userIntID) \
            .filter(Product.productID == product_uid,
                    User.tenantID == g.tenant_uid).first()
        if not product:
            raise DataNotFound(field='productID')
        in_data['cloudProtocol'] = product.cloudProtocol
        in_data['productIntID'] = product.id
        if product.cloudProtocol != 7:
            in_data['modBusIndex'] = None
        if product.cloudProtocol == 4:
            in_data = self.load_and_validate_lora(in_data)
        else:
            in_data['lora'] = None
        return in_data

    @post_dump
    def dump_device(self, data):

        lora = data.get('lora')
        # LoRa OTAA data process
        if lora and lora.get('type') == 'otaa':
            data['lora'] = LoRaOTTASchema().dump(lora).data
        return data


class DeviceUpdateSchema(DeviceSchema):
    """ The overriding fields cannot be updated """

    deviceID = EmqString(dump_only=True)  # lora device allows updating deviceID
    deviceUsername = EmqString(dump_only=True)
    token = EmqString(dump_only=True)
    IMEI = EmqString(dump_only=True, len_max=15)


class GatewaySchema(ClientSchema):
    deviceName = EmqString(required=True, dump_to='gatewayName', load_from='gatewayName')
    mac = EmqString(allow_none=True)
    gatewayProtocol = EmqInteger(allow_none=True)
    gatewayModel = EmqString(allow_none=True)
    upLinkNetwork = EmqInteger(required=True, validate=OneOf(range(1, 8)))

    @validates('deviceName')
    def is_exist(self, value):
        if self._validate_obj('deviceName', value):
            return
        query = db.session.query(Gateway.id) \
            .filter(Gateway.tenantID == g.tenant_uid,
                    Gateway.deviceName == value).first()
        if query:
            raise DataExisted(field='gatewayName')

    @pre_load
    def handle_pre_load(self, in_data):

        product_uid = in_data.get('productID')
        if not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        self.validate_create_permission(product_uid)
        product = db.session \
            .query(Product.cloudProtocol, Product.id, Product.gatewayProtocol) \
            .join(User, User.id == Product.userIntID) \
            .filter(Product.productID == product_uid,
                    User.tenantID == g.tenant_uid).first()
        if not product:
            raise DataNotFound(field='productID')
        if product.gatewayProtocol == 4:
            if not in_data.get('mac'):
                raise FormInvalid(field='mac')
        elif product.gatewayProtocol == 7:
            if in_data.get('gatewayModel') not in ['Neuron']:
                raise FormInvalid(field='gatewayModel')
        in_data['cloudProtocol'] = product.cloudProtocol
        in_data['gatewayProtocol'] = product.gatewayProtocol
        in_data['productIntID'] = product.id
        return in_data


class GatewayUpdateSchema(GatewaySchema):
    deviceID = EmqString(dump_only=True)
    deviceUsername = EmqString(dump_only=True)
    token = EmqString(dump_only=True)


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
    clients = EmqList(required=True, list_type=int)

    @post_load
    def handle_loads(self, data):
        group_id = request.view_args.get('group_id')
        clients_id = data['clients']
        group_clients_id = db.session.query(GroupClient.c.clientIntID) \
            .join(Group, Group.groupID == GroupClient.c.groupID) \
            .filter(Group.id == group_id).all()
        add_clients_id = set(clients_id).difference(set(group_clients_id))
        if len(group_clients_id) + len(add_clients_id) > 1001:
            raise ResourceLimited(field='clients')
        clients = Client.query.filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Client.id.in_(add_clients_id)).all()
        if len(clients) != len(add_clients_id):
            raise DataNotFound(field='clients')
        data['clients'] = clients
        return data


class ChannelSchema(BaseSchema):
    channelType = EmqString(required=True, validate=OneOf(['COM', 'TCP']))
    drive = EmqString(required=True)  # gateway driver
    COM = EmqString(allow_none=True)  # COM
    Baud = EmqInteger(allow_none=True)  # Baud
    Data = EmqInteger(allow_none=True)  # 6/7/8
    Stop = EmqString(allow_none=True)  # 1/1.5/2
    Parity = EmqString(allow_none=True)  # N/O/E
    IP = EmqString(allow_none=True)  # TCP, ip
    Port = EmqInteger(allow_none=True)  # TCP, port

    @post_load(pass_original=True)
    def channel_load(self, out_data, original_data):
        if out_data['channelType'] == 'COM':
            out_data = ChannelComSchema().load(out_data).data
        elif out_data['channelType'] == 'TCP':
            out_data = ChannelTcpSchema().load(out_data).data
        out_data['channelType'] = original_data.get('channelType')
        out_data['drive'] = original_data.get('drive')
        return out_data


class ChannelComSchema(BaseSchema):
    COM = EmqString(required=True)  # COM
    Baud = EmqInteger(required=True, validate=OneOf(
        [0, 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800,
         2400, 4800, 9600, 19200, 38400, 57600, 115200]
    ))  # Baud
    Data = EmqInteger(required=True, validate=OneOf([6, 7, 8]))  # 6/7/8
    Stop = EmqString(require=True,
                     validate=OneOf(['1', '1.5', '2']))  # 1/1.5/2
    Parity = EmqString(required=True, validate=OneOf(['N', 'O', 'E']))  # N/O/E


class ChannelTcpSchema(BaseSchema):
    IP = EmqString(required=True)  # TCP，服务器
    Port = EmqInteger(required=True)  # TCP，端口

    @validates('IP')
    def check_ip(self, value):
        pat = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if not pat.match(value):
            raise FormInvalid('IP')


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


class CertClientSchema(BaseSchema):
    clients = EmqList(required=True, list_type=int)

    @post_load
    def handle_cert_clients(self, data):
        clients_id = data['clients']
        clients = Client.query \
            .filter(Client.id.in_(set(clients_id)), Client.authType == 2) \
            .many(allow_none=False, expect_result=len(clients_id))
        cert_id = self.get_origin_obj('id')
        exist_cert_clients = db.session \
            .query(func.count(CertClient.c.clientIntID)) \
            .filter(CertClient.c.certIntID == cert_id,
                    CertClient.c.clientIntID.in_(set(clients_id))) \
            .scalar()
        if exist_cert_clients:
            raise DataExisted(field='clients')
        data['clients'] = clients
        return data


class DeviceLocationSchema(BaseSchema):
    longitude = EmqFloat(allow_none=True)
    latitude = EmqFloat(allow_none=True)
    location = EmqString(allow_none=True, len_max=300)


class AddDeviceSchema(BaseSchema):
    devicesIntID = EmqList(required=True)


class DeviceIdsSchema(BaseSchema):
    ids = EmqList(required=True, list_type=int)


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


class LoRaSchema(BaseSchema):
    type = EmqString(required=True, validate=lambda x: x in ['otaa', 'abp'])
    region = EmqString(allow_none=True)
    fcntCheck = EmqInteger(allow_none=True)

    @validates('region')
    def validate_region(self, value):
        if value is None:
            return
        cache = Cache()
        dict_code_cache = cache.dict_code
        region_cache = dict_code_cache['region']
        if value not in region_cache.keys():
            raise DataNotFound(field='region')

    @validates('fcntCheck')
    def validate_fcnt_check(self, value):
        if value is None:
            return
        cache = Cache()
        dict_code_cache = cache.dict_code
        fcnt_check_cache = dict_code_cache['fcntCheck']
        if value not in fcnt_check_cache.keys():
            raise DataNotFound(field='fcntCheck')


class LoRaOTTASchema(LoRaSchema):
    region = EmqString(required=True)
    appEUI = EmqString(required=True, validate=validate.Length(equal=16))
    appKey = EmqString(required=True, validate=validate.Length(equal=32))
    fcntCheck = EmqInteger(required=True)
    canJoin = fields.Boolean(required=True)

    @post_dump
    def dump_can_join(self, data):
        # bool to 0/1
        data['canJoin'] = 1 if data.get('canJoin') else 0
        return data


class LoRaABPSchema(LoRaSchema):
    region = EmqString(required=True)
    nwkSKey = EmqString(required=True, validate=validate.Length(equal=32))
    appSKey = EmqString(required=True, validate=validate.Length(equal=32))
    fcntUp = EmqInteger(required=True)
    fcntDown = EmqInteger(required=True)
    fcntCheck = EmqInteger(required=True)
