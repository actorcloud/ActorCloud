from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, ModelMixin, db
from actor_libs.utils import generate_uuid


__all__ = [
    'Device', 'EndDevice', 'Gateway', 'Group', 'GroupDevice',
    'Cert', 'CertDevice', 'Channel', 'Lwm2mObject', 'Lwm2mItem',
    'DeviceCountHour', 'DeviceCountDay', 'DeviceCountMonth',
    'EmqxBill', 'EmqxBillHour', 'EmqxBillDay', 'EmqxBillMonth'
]


def random_group_uid():
    """ Generate a 6-bit group identifier """

    group_uid = generate_uuid(size=6)
    group = db.session.query(db.func.count(Group.id)) \
        .filter(Group.groupID == group_uid).scalar()
    if group:
        group_uid = random_group_uid()
    return group_uid


GroupDevice = db.Table(
    'groups_devices',
    db.Column('deviceIntID', db.Integer,
              db.ForeignKey('devices.id', onupdate="CASCADE", ondelete="CASCADE"),
              primary_key=True),
    db.Column('groupID', db.String(6), db.ForeignKey('groups.groupID'), primary_key=True),
)

CertDevice = db.Table(
    'certs_devices',
    db.Column('deviceIntID', db.Integer,
              db.ForeignKey('devices.id', onupdate="CASCADE", ondelete="CASCADE"),
              primary_key=True),
    db.Column('certIntID', db.Integer, db.ForeignKey('certs.id'), primary_key=True),
)


class Device(BaseModel):
    __tablename__ = 'devices'
    deviceName = db.Column(db.String(50))
    deviceType = db.Column(db.Integer)  # 1:end_device 2:gateway
    deviceID = db.Column(db.String(50))
    deviceUsername = db.Column(db.String(50))
    token = db.Column(db.String(50), default=generate_uuid)
    authType = db.Column(db.SmallInteger)  # 1:token 2:cert
    lastConnection = db.Column(db.DateTime)
    blocked = db.Column(db.SmallInteger, server_default='0')  # 0:false 1:true
    deviceStatus = db.Column(db.SmallInteger, server_default='0')  # 0:offline 1:online 2:sleep
    location = db.Column(db.String(300))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    softVersion = db.Column(db.String(50))
    hardwareVersion = db.Column(db.String(50))
    manufacturer = db.Column(db.String(50))
    serialNumber = db.Column(db.String(100))
    deviceConsoleIP = db.Column(db.String(50))
    deviceConsoleUsername = db.Column(db.String(50))
    deviceConsolePort = db.Column(db.Integer, server_default='22')
    carrier = db.Column(db.Integer, server_default='1')
    upLinkNetwork = db.Column(db.Integer)  # 1:2G, 2:3G.....
    description = db.Column(db.String(300))
    mac = db.Column(db.String(50))
    metaData = db.Column(JSONB)  # meta data
    groups = db.relationship('Group', secondary=GroupDevice, lazy='dynamic')  # device groups
    certs = db.relationship('Cert', secondary=CertDevice, lazy='dynamic')  # device certs
    productID = db.Column(db.String, db.ForeignKey('products.productID'))
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    tenantID = db.Column(db.String, db.ForeignKey('tenants.tenantID',
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))
    __mapper_args__ = {'polymorphic_on': deviceType}


class EndDevice(Device):
    __tablename__ = 'end_devices'
    id = db.Column(db.Integer, db.ForeignKey('devices.id',
                                             onupdate="CASCADE",
                                             ondelete="CASCADE"), primary_key=True)
    loraData = db.Column(JSONB)  # lora protocol extend
    modbusData = db.Column(JSONB)  # modbus protocol extend
    lwm2mData = db.Column(JSONB)  # lwm2m protocol extend
    upLinkSystem = db.Column(db.SmallInteger, server_default='1')  # 1:cloud 2:gateway, 3:endDevice
    gateway = db.Column(db.Integer, db.ForeignKey('gateways.id'))  # gateway
    parentDevice = db.Column(db.Integer,
                             db.ForeignKey('end_devices.id',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"))
    __mapper_args__ = {'polymorphic_identity': 1}


class Gateway(Device):
    __tablename__ = 'gateways'
    id = db.Column(db.Integer, db.ForeignKey('devices.id',
                                             onupdate="CASCADE",
                                             ondelete="CASCADE"), primary_key=True)
    devices = db.relationship('EndDevice', foreign_keys="EndDevice.gateway", lazy='dynamic')  # 设备
    channels = db.relationship('Channel', foreign_keys="Channel.gateway")  # 通道
    __mapper_args__ = {'polymorphic_identity': 2}


class Group(BaseModel):
    __tablename__ = 'groups'
    groupID = db.Column(db.String(6), default=random_group_uid, unique=True)
    groupName = db.Column(db.String(50))
    description = db.Column(db.String(300))
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    devices = db.relationship('Device', secondary=GroupDevice, lazy='dynamic')  # group devices


class Cert(BaseModel):
    __tablename__ = 'certs'
    certName = db.Column(db.String)
    enable = db.Column(db.SmallInteger, default=1)
    CN = db.Column(db.String(36))
    key = db.Column(db.Text)  # key file string
    cert = db.Column(db.Text)  # cert file string
    devices = db.relationship('Device', secondary=CertDevice, lazy='dynamic')  # cert devices
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))


class Channel(BaseModel):
    __tablename__ = 'channels'
    channelType = db.Column(db.String)  # 1:COM，2:TCP
    drive = db.Column(db.String)
    COM = db.Column(db.String)
    Baud = db.Column(db.Integer)  # Baud
    Data = db.Column(db.Integer)  # 6/7/8
    Stop = db.Column(db.String)  # 1/1.5/2
    Parity = db.Column(db.String)  # N/O/E
    IP = db.Column(db.String)
    Port = db.Column(db.Integer)
    gateway = db.Column(db.Integer, db.ForeignKey('gateways.id'))


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
