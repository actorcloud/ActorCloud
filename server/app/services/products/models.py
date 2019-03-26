from sqlalchemy.dialects.postgresql.json import JSONB

from actor_libs.database.orm import BaseModel, db


__all__ = [
    'StreamPoint', 'DataStream', 'DataPoint', 'ProductResource',
    'AppTemplate', 'Codec'
]


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


class ProductResource(BaseModel):
    __tablename__ = 'product_resources'
    codeValue = db.Column(db.String(50))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    dataPointID = db.Column(db.String)
    dataPointIntID = db.Column(db.Integer,
                               db.ForeignKey('data_points.id',
                                             onupdate="CASCADE",
                                             ondelete="CASCADE"))
    productItemIntID = db.Column(db.Integer,
                                 db.ForeignKey('product_items.id',
                                               onupdate="CASCADE",
                                               ondelete="CASCADE"))


class AppTemplate(BaseModel):
    __tablename__ = 'app_templates'
    templateName = db.Column(db.String(50))  # 模板名称
    templateType = db.Column(db.Integer)  # 模板格式，1:开关，2:枚举(MQTT)，3:数值，4:字符串，5:布尔,# 6:时间（LWM2M）
    instanceID = db.Column(db.Integer)  # 关联LWM2M协议设备时的实例 ID
    places = db.Column(JSONB)  # 页面位置
    defaultValues = db.Column(JSONB)  # 同一数据流下其它功能点默认值
    dataPointIntID = db.Column(db.Integer,
                               db.ForeignKey('data_points.id',
                                             onupdate="CASCADE",
                                             ondelete="CASCADE"))
    dataStreamIntID = db.Column(db.Integer,
                                db.ForeignKey('data_streams.id',
                                              onupdate="CASCADE",
                                              ondelete="CASCADE"))
    productItemIntID = db.Column(db.Integer,
                                 db.ForeignKey('product_items.id',
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
