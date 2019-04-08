from sqlalchemy.dialects.postgresql.json import JSONB

from actor_libs.database.orm import BaseModel, db
from actor_libs.utils import generate_uuid


__all__ = [
    'Product', 'StreamPoint', 'DataStream', 'DataPoint', 'Codec'
]


def random_product_uid():
    """ Generate a 6-bit product identifier """

    product_uid = generate_uuid(size=6, str_type='char')
    product = db.session.query(func.count(Product.id)) \
        .filter(Product.productID == product_uid).scalar()
    if product:
        product_uid = random_product_uid()
    return product_uid


class Product(BaseModel):
    """
    cloudProtocol: 1:MQTT，2:CoAp，3:LwM2M，4:LoRaWAN，5:HTTP，6:WebSocket
    """
    __tablename__ = 'products'
    productID = db.Column(db.String(6), default=random_product_uid, unique=True)  # 产品标识
    productName = db.Column(db.String(50))  # 产品名称
    description = db.Column(db.String(300))  # 产品描述
    cloudProtocol = db.Column(db.SmallInteger, server_default='1')  # 云端协议, 网关类型产品显示为上联协议
    gatewayProtocol = db.Column(db.Integer)  # 网关协议
    productType = db.Column(db.SmallInteger, server_default='1')  # 产品类型1:设备，2:网关
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    devices = db.relationship('Client', backref='products', lazy='dynamic')


class StreamPoint(db.Model):
    __tablename__ = 'streams_points'
    dataStreamIntID = db.Column(db.Integer,
                                db.ForeignKey('data_streams.id',
                                              onupdate="CASCADE",
                                              ondelete="CASCADE"),
                                primary_key=True)
    dataPointIntID = db.Column(db.Integer, db.ForeignKey('data_points.id'), primary_key=True)
    binaryPointOrder = db.Column(db.Integer)
    dataPoint = db.relationship("DataPoint", back_populates="dataStreams")
    dataStream = db.relationship("DataStream", back_populates="dataPoints")


class DataStream(BaseModel):
    __tablename__ = 'data_streams'
    streamName = db.Column(db.String(50))  # 数据流名称
    streamType = db.Column(db.SmallInteger)  # 流类型
    streamDataType = db.Column(db.SmallInteger, server_default='1')  # 数据类型 1 json, 2 二进制
    topic = db.Column(db.String(500))  # 数据流主题
    detail = db.Column(db.Text)  # 备注
    streamID = db.Column(db.Integer)
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))  # 创建人id
    productID = db.Column(db.String, db.ForeignKey('products.productID'))  # 产品ID外键
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    dataPoints = db.relationship("StreamPoint", back_populates="dataStream")


class DataPoint(BaseModel):
    __tablename__ = 'data_points'
    dataPointName = db.Column(db.String(50))  # 功能点名称
    dataPointID = db.Column(db.String(50))  # 功能点标识
    dataTransType = db.Column(db.Integer)  # 数据传输类型(上报，下发, 上报下发)
    pointDataType = db.Column(db.Integer)  # 数据格式: json(1~10), 二进制其他类型(11~)
    isLocationType = db.Column(db.SmallInteger)  # 是否为位置类型去除默认值(1是)
    locationType = db.Column(db.SmallInteger)  # 位置类型(1 经度, 2 纬度, 3 海拔)
    detail = db.Column(db.Text)  # 备注
    unitName = db.Column(db.String(50))  # 单位名称(数据类型为数值类型<1>必填)
    unitSymbol = db.Column(db.String(50))  # 单位符号(同上)
    lowerLimit = db.Column(db.Float)  # 下限(同上)
    upperLimit = db.Column(db.Float)  # 上限(同上)
    dataStep = db.Column(db.Float)  # 数据步长(同上)
    enum = db.Column(db.JSON, default=[])  # 枚举值 (数据类型为枚举类型<2>必填)
    faultValue = db.Column(db.String(100))  # 故障值(数据类型为故障类型<4>必填)
    isDiscard = db.Column(db.SmallInteger)  # 是否丢弃该消息 (数据类型为故障类型<4>必填)
    binarySize = db.Column(db.Integer)  # 二进制长度(数值类型为二进制<11~>时才选择其他为空)
    registerAddr = db.Column(db.String)  # 寄存器地址
    decimal = db.Column(db.SmallInteger)  # 小数位（数据类型为长整型（21）必填）
    dataStreams = db.relationship("StreamPoint", back_populates="dataPoint")
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    productID = db.Column(db.String, db.ForeignKey('products.productID'))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class Codec(BaseModel):
    __tablename__ = 'codec'
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    code = db.Column(JSONB)
    codeStatus = db.Column(db.SmallInteger, server_default='1')  # 代码状态，1:待审核 2:审核成功 3:审核失败
    reviewOpinion = db.Column(db.String)
