import random
import string

from sqlalchemy import JSON, func
from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, ModelMixin, db
from actor_libs.utils import generate_uuid


__all__ = [
    'Client', 'Device', 'Gateway', 'Group', 'GroupClient',
    'Policy', 'MqttAcl', 'Cert', 'CertAuth', 'MqttSub',
    'EmqxBill', 'EmqxBillHour', 'EmqxBillDay', 'EmqxBillMonth',
    'DeviceCountHour', 'DeviceCountDay', 'DeviceCountMonth',
    'UploadInfo', 'Lwm2mObject', 'Lwm2mItem', 'Gateway', 'Channel'
]


def random_group_uid():
    """ Generate a 6-bit group identifier """

    group_uid = ''.join([
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    ])
    group = db.session.query(func.count(Group.id)) \
        .filter(Group.groupID == group_uid).scalar()
    if group:
        group_uid = random_group_uid()
    return group_uid


GroupClient = db.Table(
    'groups_clients',
    db.Column('clientIntID', db.Integer,
              db.ForeignKey('clients.id', onupdate="CASCADE", ondelete="CASCADE"),
              primary_key=True),
    db.Column('groupID', db.String(6), db.ForeignKey('groups.groupID'), primary_key=True),
)


class Client(BaseModel):
    __tablename__ = 'clients'
    deviceID = db.Column(db.String(50))
    deviceName = db.Column(db.String(50))
    softVersion = db.Column(db.String(50))
    hardwareVersion = db.Column(db.String(50))
    manufacturer = db.Column(db.String(50))
    serialNumber = db.Column(db.String(100))
    location = db.Column(db.String(300))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    deviceUsername = db.Column(db.String(50))
    token = db.Column(db.String(50), default=generate_uuid)
    authType = db.Column(db.SmallInteger)  # 1:token 2:cert
    deviceStatus = db.Column(db.SmallInteger,
                             server_default='0')  # 0:offline 1:online 2:sleep
    deviceConsoleIP = db.Column(db.String(50))
    deviceConsoleUsername = db.Column(db.String(50))
    deviceConsolePort = db.Column(db.Integer, server_default='22')
    upLinkSystem = db.Column(db.SmallInteger, server_default='1')  # 1:cloud 2:gateway
    IMEI = db.Column(db.String(15))
    IMSI = db.Column(db.String(100))
    carrier = db.Column(db.Integer, server_default='1')
    physicalNetwork = db.Column(db.Integer, server_default='1')
    blocked = db.Column(db.SmallInteger, server_default='0')  # 0:false 1:true
    autoSub = db.Column(db.Integer)  # 0:disable 1:enable
    description = db.Column(db.String(300))
    mac = db.Column(db.String(50))  #
    clientType = db.Column(db.Integer)  # 1:device 2:gateway
    lastConnection = db.Column(db.DateTime)
    groups = db.relationship('Group', secondary=GroupClient)  # client groups
    productID = db.Column(db.String, db.ForeignKey('products.productID'))
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    tenantID = db.Column(db.String, db.ForeignKey('tenants.tenantID',
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))
    __mapper_args__ = {'polymorphic_on': clientType}


class Device(Client):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, db.ForeignKey('clients.id'), primary_key=True)
    lora = db.Column(JSONB)
    metaData = db.Column(JSONB)  # meta data
    modBusIndex = db.Column(db.SmallInteger)  # Modbus device index
    gateway = db.Column(db.Integer, db.ForeignKey('gateways.id'))  # gateway
    parentDevice = db.Column(db.Integer,
                             db.ForeignKey('devices.id',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"))
    __mapper_args__ = {'polymorphic_identity': 1}


class Gateway(Client):
    __tablename__ = 'gateways'
    id = db.Column(db.Integer, db.ForeignKey('clients.id'), primary_key=True)
    gatewayModel = db.Column(db.String)  # 网关型号
    upLinkNetwork = db.Column(db.Integer)  # 上联网络
    devices = db.relationship('Device', foreign_keys="Device.gateway")  # 设备
    channels = db.relationship('Channel', foreign_keys="Channel.gateway")  # 通道
    __mapper_args__ = {'polymorphic_identity': 2}


class Group(BaseModel):
    __tablename__ = 'groups'
    groupID = db.Column(db.String(6), default=random_group_uid, unique=True)
    groupName = db.Column(db.String(50))
    description = db.Column(db.String(300))
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    clients = db.relationship('Client', secondary=GroupClient, lazy='dynamic')  # group clients


class Policy(BaseModel):
    __tablename__ = 'policies'
    name = db.Column(db.String(50))  # 名称
    access = db.Column(db.SmallInteger)  # 操作
    allow = db.Column(db.SmallInteger)  # 访问控制
    description = db.Column(db.String(300))  # 描述
    topic = db.Column(db.String(500))  # 主题
    mqtt_acl = db.relationship('MqttAcl', backref='policies', passive_deletes=True, lazy=True)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))  # 用户id


class MqttAcl(BaseModel):
    __tablename__ = 'mqtt_acl'
    ipaddr = db.Column(db.String(50))  # ip地址
    allow = db.Column(db.SmallInteger)  # 访问控制
    username = db.Column(db.String(100))  # 名称
    access = db.Column(db.SmallInteger)  # 操作
    clientID = db.Column(db.String(100))  # 客户端uid tenantID:productID:deviceID
    topic = db.Column(db.String(500))  # 主题
    deviceIntID = db.Column(db.Integer, db.ForeignKey(
        'clients.id', onupdate="CASCADE", ondelete="CASCADE"))  # 设备id
    policyIntID = db.Column(db.Integer, db.ForeignKey(
        'policies.id', onupdate="CASCADE", ondelete="CASCADE"))  # 策略 id


class Cert(BaseModel):
    __tablename__ = 'certs'
    name = db.Column(db.String)
    enable = db.Column(db.SmallInteger, default=1)  # 是否可用
    CN = db.Column(db.String(36), unique=True)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    key = db.Column(db.String(2000))  # key file string
    cert = db.Column(db.String(2000))  # cert file string


class CertAuth(BaseModel):
    __tablename__ = 'cert_auth'
    deviceIntID = db.Column(db.Integer,
                            db.ForeignKey('clients.id', onupdate="CASCADE", ondelete="CASCADE"))
    CN = db.Column(db.String,
                   db.ForeignKey('certs.CN',
                                 onupdate="CASCADE", ondelete="CASCADE"))


class MqttSub(BaseModel):
    __tablename__ = 'mqtt_sub'
    clientID = db.Column(db.String(100))
    topic = db.Column(db.String(500))
    qos = db.Column(db.SmallInteger, default=1)
    deviceIntID = db.Column(db.Integer, db.ForeignKey(
        'clients.id', onupdate="CASCADE", ondelete="CASCADE"))


EmqxBill = db.Table(
    'emqx_bills',
    db.Column('msgTime', db.DateTime, nullable=False),  # 消息时间
    db.Column('tenantID', db.String(9)),  # 租户ID
    db.Column('productID', db.String(6)),  # 产品 ID
    db.Column('deviceID', db.String(100)),  # 设备ID
    db.Column('msgType', db.SmallInteger),  # 1登录，2订阅，3取消订阅，4发布，5接收
    db.Column('msgSize', db.Integer),  # 消息大小
    db.Index('emqx_bills_msgTime_idx', 'msgTime'),
    db.Index('emqx_bills_union_idx', 'msgTime', 'tenantID', 'deviceID', 'msgType')
)


class EmqxBillHour(ModelMixin, db.Model):
    __tablename__ = 'emqx_bills_hour'
    __table_args__ = (
        db.Index('emqx_bills_hour_countTime_idx', "countTime"),
    )
    msgType = db.Column(db.Integer, primary_key=True)  # 消息类型
    msgCount = db.Column(db.Integer)  # 小时消息数量
    msgSize = db.Column(db.Integer)  # 小时消息流量
    countTime = db.Column(db.DateTime, primary_key=True)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)


class EmqxBillDay(BaseModel):
    __tablename__ = 'emqx_bills_day'
    msgType = db.Column(db.Integer)  # 消息类型
    msgCount = db.Column(db.Integer)  # 小时消息数量
    msgSize = db.Column(db.Integer)  # 小时消息流量
    countTime = db.Column(db.DateTime)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"))


class EmqxBillMonth(BaseModel):
    __tablename__ = 'emqx_bills_month'
    msgType = db.Column(db.Integer)  # 消息类型
    msgCount = db.Column(db.Integer)  # 月消息数量
    msgSize = db.Column(db.Integer)  # 月消息流量
    countTime = db.Column(db.DateTime)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"))


class DeviceCountHour(BaseModel):
    __tablename__ = 'device_count_hour'
    deviceCount = db.Column(db.Integer)  # 小时设备数量
    deviceOnlineCount = db.Column(db.Integer)  # 小时设备在线数量
    deviceOfflineCount = db.Column(db.Integer)  # 小时离线设备数量
    deviceSleepCount = db.Column(db.Integer)  # 休眠设备数
    countTime = db.Column(db.DateTime)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"))


class DeviceCountDay(BaseModel):
    ___tablename__ = 'device_count_day'
    deviceCount = db.Column(db.Integer)  # 日设备数量
    deviceOnlineCount = db.Column(db.Integer)  # 日在线数量
    deviceOfflineCount = db.Column(db.Integer)  # 日设备数量
    deviceSleepCount = db.Column(db.Integer)  # 休眠设备数
    countTime = db.Column(db.DateTime)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"))


class DeviceCountMonth(BaseModel):
    __tablename__ = 'device_count_month'
    deviceCount = db.Column(db.Integer)  # 月设备数量
    deviceOnlineCount = db.Column(db.Integer)  # 日设备在线数量
    deviceOfflineCount = db.Column(db.Integer)  # 日离线设备数量
    deviceSleepCount = db.Column(db.Integer)  # 休眠设备数
    countTime = db.Column(db.DateTime)  # 统计时间
    tenantID = db.Column(db.String, db.ForeignKey(
        'tenants.tenantID', onupdate="CASCADE", ondelete="CASCADE"))


class UploadInfo(BaseModel):
    __tablename__ = 'upload_info'
    fileName = db.Column(db.String(300))  # 文件名称
    displayName = db.Column(db.String(300))  # 文件原始名称
    fileType = db.Column(db.SmallInteger, default=1)  # 文件类型：1压缩包, 2图片
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人ID外键


class Lwm2mObject(BaseModel):
    __tablename__ = 'lwm2m_objects'
    objectName = db.Column(db.String)  # 对象名
    objectID = db.Column(db.Integer, unique=True)  # 对象int型ID
    description = db.Column(db.String)  # 对象描述
    objectURN = db.Column(db.String)  # 对象URN
    objectVersion = db.Column(db.String)  # 对象版本
    multipleInstance = db.Column(db.String)  # Multiple表示有多个实例，Single表示单个实例
    mandatory = db.Column(db.String)  # 强制性，Optional表示可选，Mandatory表示强制


class Lwm2mItem(BaseModel):
    __tablename__ = 'lwm2m_items'
    itemName = db.Column(db.String)  # 属性名
    itemID = db.Column(db.Integer)  # 属性int型ID
    objectItem = db.Column(db.String)  # /objectID/itemID
    description = db.Column(db.String)  # 属性描述
    itemType = db.Column(db.String)  # 属性类型
    itemOperations = db.Column(db.String)  # 支持操作，R/W/RW/E
    itemUnit = db.Column(db.String)  # 单位
    rangeEnumeration = db.Column(db.String)  # 属性的值范围
    mandatory = db.Column(db.String)  # 强制性，Optional表示可选，Mandatory表示强制
    multipleInstance = db.Column(db.String)  # Multiple表示有多个实例，Single表示单个实例
    objectID = db.Column(db.Integer,
                         db.ForeignKey('lwm2m_objects.objectID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class Channel(BaseModel):
    __tablename__ = 'channels'
    channelType = db.Column(db.String)  # 通道类型， 1:COM，2:TCP
    drive = db.Column(db.String)  # 网关驱动
    COM = db.Column(db.String)  # COM
    Baud = db.Column(db.Integer)  # Baud
    Data = db.Column(db.Integer)  # 6/7/8
    Stop = db.Column(db.String)  # 1/1.5/2
    Parity = db.Column(db.String)  # N/O/E
    IP = db.Column(db.String)  # TCP, 服务器ip
    Port = db.Column(db.Integer)  # TCP, 端口
    gateway = db.Column(db.Integer, db.ForeignKey('gateways.id'))
