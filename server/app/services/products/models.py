from sqlalchemy.dialects.postgresql.json import JSONB

from actor_libs.database.orm import BaseModel, db
from actor_libs.utils import generate_uuid


__all__ = [
    'Product', 'StreamPoint', 'DataStream', 'DataPoint', 'Codec'
]


def random_product_uid():
    """ Generate a 6-bit product identifier """

    product_uid = generate_uuid(size=6, str_type='char')
    product = db.session.query(Product.id) \
        .filter(Product.productID == product_uid).first()
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
    devices = db.relationship('Device', backref='products', lazy='dynamic')


StreamPoint = db.Table(
    'streams_points',
    db.Column('dataPointIntID',
              db.Integer,
              db.ForeignKey('data_points.id'), primary_key=True),
    db.Column('dataStreamIntID',
              db.Integer,
              db.ForeignKey('data_streams.id',
                            onupdate="CASCADE",
                            ondelete="CASCADE"), primary_key=True),
)


class DataStream(BaseModel):
    __tablename__ = 'data_streams'
    streamID = db.Column(db.String(50))  # data stream identifier
    streamName = db.Column(db.String(50))
    streamType = db.Column(db.SmallInteger)  # 1:deviceUp, 2:deviceDown
    topic = db.Column(db.String(500))
    description = db.Column(db.String(300))
    dataPoints = db.relationship('DataPoint', secondary=StreamPoint,
                                 backref=db.backref('dataStreams', lazy='dynamic'))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    productID = db.Column(db.String, db.ForeignKey('products.productID'))
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))


class DataPoint(BaseModel):
    __tablename__ = 'data_points'
    dataPointName = db.Column(db.String(50))
    dataPointID = db.Column(db.String(50))
    dataTransType = db.Column(db.Integer)  # 1: Up, 2: Down, 3 UpAndDown
    pointDataType = db.Column(db.Integer)  # 1:num, 2:str, 3:Boolean, 4:time, 5:location
    extendTypeAttr = db.Column(JSONB, server_default='{}')  # extension attr for point data type
    isLocationType = db.Column(db.SmallInteger, server_default='0')  # is location-> 0:no, 1:yes
    locationType = db.Column(db.SmallInteger)  # 1: longitude, 2: latitude, 3: altitude
    enum = db.Column(db.JSON, server_default='[]')  # enum of string or integer
    registerAddr = db.Column(db.String)  # modbus product require
    description = db.Column(db.String(300))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    productID = db.Column(db.String, db.ForeignKey('products.productID'))
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))


class Codec(BaseModel):
    __tablename__ = 'codec'
    code = db.Column(JSONB)
    reviewOpinion = db.Column(db.String)
    codeStatus = db.Column(db.SmallInteger, server_default='1')  # 1:Pending, 2:Success, 3:Failed
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
