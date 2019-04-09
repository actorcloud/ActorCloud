import re

from flask import request, g
from marshmallow import validates, pre_load, validates_schema
from marshmallow.validate import OneOf

from actor_libs.database.orm import db
from actor_libs.errors import DataExisted, FormInvalid, DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger, EmqList, EmqFloat, EmqDict
)
from app.models import (
    User, Product, DataStream, DataPoint
)


__all__ = [
    'ProductSchema', 'UpdateProductSchema', 'ProductSubSchema',
    'DataPointSchema', 'DataPointUpdateSchema', 'DataStreamSchema',
    'UpdateDataStreamSchema'
]


class ProductSchema(BaseSchema):
    productID = EmqString(dump_only=True)
    productName = EmqString(required=True)
    description = EmqString(allow_none=True, len_max=300)
    cloudProtocol = EmqInteger(required=True, validate=OneOf(range(1, 8)))
    gatewayProtocol = EmqInteger(allow_none=True, validate=OneOf(range(1, 8)))
    productType = EmqInteger(required=True, validate=OneOf([1, 2]))

    @validates('productName')
    def is_exist(self, value):
        if self._validate_obj('productName', value):
            return
        product_name = db.session.query(Product.productName) \
            .filter_tenant(tenant_uid=g.tenant_uid)\
            .filter(Product.productName == value).first()
        if product_name:
            raise DataExisted(field='productName')

    @pre_load
    def product_load(self, data):
        product_type = data.get('productType')
        if not product_type:
            data['productType'] = 1
        gateway_protocol = data.get('gatewayProtocol')
        if data['productType'] == 2 and not gateway_protocol:
            raise FormInvalid(field='gatewayProtocol')
        if data['productType'] == 1 and gateway_protocol:
            data['gatewayProtocol'] = None
        return data


class UpdateProductSchema(ProductSchema):
    cloudProtocol = EmqInteger(dump_only=True)
    gatewayProtocol = EmqInteger(dump_only=True)
    productType = EmqInteger(dump_only=True)

    @pre_load
    def product_load(self, data):
        return data


class ProductSubSchema(BaseSchema):
    topic = EmqString(required=True)
    qos = EmqInteger(allow_none=True)


class DataPointSchema(BaseSchema):
    dataPointName = EmqString(required=True)
    dataPointID = EmqString(required=True, len_max=50)
    dataTransType = EmqInteger(required=True)  # 1: Up, 2: Down, 3 UpAndDown
    pointDataType = EmqInteger(required=True)  # 1~10: json, (11~): binary
    isLocationType = EmqInteger(required=True)  # 1:yes, 2:no
    locationType = EmqInteger(allow_none=True)  # 1: longitude, 2: latitude, 3: altitude
    detail = EmqString(allow_none=True, len_max=300)
    unitName = EmqString(allow_none=True)  # if pointDataType is 1, require
    unitSymbol = EmqString(allow_none=True)  # if pointDataType is 1, require
    lowerLimit = EmqFloat(allow_none=True)  # if pointDataType is 1, require
    upperLimit = EmqFloat(allow_none=True)  # if pointDataType is 1, require
    dataStep = EmqFloat(allow_none=True)  # if pointDataType is 1, require
    enum = EmqList(allow_none=True)  # enum of string or integer
    decimal = EmqInteger(allow_none=True)  # if pointDataType is 21(longint) require
    faultValue = EmqString(allow_none=True, len_max=100)  # if pointDataType is 1(fault), require
    isDiscard = EmqInteger(allow_none=True)  # if pointDataType is 1(fault), require
    binarySize = EmqInteger(allow_none=True)  # if pointDataType > 11 require
    registerAddr = EmqString(allow_none=True,
                             validate=lambda x: x.startswith('W'))  # modbus product require
    productID = EmqString(required=True)  # product uid
    cloudProtocol = EmqInteger(load_only=True)  # product cloudProtocol

    @validates('dataPointName')
    def name_is_exist(self, value):
        if self._validate_obj('dataPointName', value):
            return

        product_uid = self.get_request_data('productID')
        point_name = db.session.query(DataPoint.dataPointName) \
            .filter(DataPoint.productID == product_uid,
                    DataPoint.dataPointName == value).first()
        if point_name:
            raise DataExisted(field='dataPointName')

    @validates('dataPointID')
    def check_point_id(self, value):
        if self._validate_obj('dataPointID', value):
            return

        if re.match(r"^[0-9A-Za-z_\-]*$", value):
            raise FormInvalid(field='dataPointID')
        product_uid = self.get_request_data('productID')
        data_point_uid = DataPoint.query \
            .filter(DataPoint.productID == product_uid,
                    DataPoint.dataPointID == value).first()
        if data_point_uid:
            raise DataExisted(field='dataPointID')

    @validates_schema
    def validate_modbus_protocol(self, data):
        product_uid = data.get('productID')
        cloud_protocol = data.get('cloudProtocol')
        point_data_type = data.get('pointDataType')
        register_addr = data.get('registerAddr')
        decimal = data.get('decimal')

        if cloud_protocol != 7:
            return data
        # validate pointDataType
        if point_data_type not in range(21, 26):
            raise FormInvalid(field='pointDataType')
        # validate decimal
        if point_data_type == 21 and decimal is None:
            raise FormInvalid(field='decimal')
        if self._validate_obj('registerAddr', register_addr):
            return
        # validate registerAdd
        register_addr = db.session.query(DataPoint.registerAddr) \
            .filter(DataPoint.productID == product_uid,
                    DataPoint.registerAddr == register_addr) \
            .first()
        if register_addr:
            raise DataExisted(field='registerAddr')

    @pre_load
    def handle_load_data(self, data):
        data = self.handle_enum_type(data)
        data = self.set_data_type_empty(data)
        # validate product todo productID?
        product_id = data.get('productIntID')
        if not isinstance(product_id, int):
            raise FormInvalid(field='productIntID')
        product = Product.query. \
            filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.id == product_id).first()
        if not product:
            raise DataNotFound(field='productIntID')
        data['productID'] = product.productID
        data['cloudProtocol'] = product.cloudProtocol
        return data

    @staticmethod
    def handle_enum_type(data):
        enum = data.get('enum')
        point_data_type = data.get('pointDataType')

        if enum is None and point_data_type in [1, 2]:
            data['enum'] = []
        else:
            data['enum'] = None
        return data

    @staticmethod
    def set_data_type_empty(data):
        """ 将表单中非该类型(pointDataType)关联的字段为None """

        data_type_schemas = [
            'unitName', 'unitSymbol', 'lowerLimit', 'upperLimit',
            'dataStep', 'faultValue', 'isDiscard', 'binarySize', 'enum'
        ]
        data_type_schema_dict = {
            1: ['faultValue', 'isDiscard', 'binarySize'],
            3: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                'faultValue', 'isDiscard', 'binarySize'],
            4: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                'binarySize', 'enum'],
            5: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                'binarySize', 'enum', 'faultValue', 'isDiscard'],
            6: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                'faultValue', 'isDiscard', 'binarySize', 'enum'],
            11: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                 'faultValue', 'isDiscard'],
            21: ['unitName', 'unitSymbol', 'lowerLimit', 'upperLimit', 'dataStep',
                 'faultValue', 'isDiscard', 'enum']
        }

        data_type = data.get('pointDataType')
        if not isinstance(data_type, int):
            raise FormInvalid(field='pointDataType')
        is_location = data.get('isLocationType')
        if data_type > 20:
            set_empty_schemas = data_type_schema_dict.get(21)
        elif 10 < data_type < 20:
            set_empty_schemas = data_type_schema_dict.get(11)
        else:
            set_empty_schemas = data_type_schema_dict.get(data_type)
        required_schemas = set(data_type_schemas) ^ set(set_empty_schemas)
        if data_type not in [5, 6] and not set(required_schemas) & set(data.keys()):
            raise FormInvalid(field='pointDataType')
        if not isinstance(is_location, int):
            raise FormInvalid(field='isLocationType')
        if is_location != 1:
            set_empty_schemas.append('locationType')
        for key, value in data.items():
            if key in set_empty_schemas:
                data[key] = None
        return data


class DataPointUpdateSchema(DataPointSchema):
    """功能点更新表单验证"""

    dataPointID = EmqString(dump_only=True)
    productID = EmqString(dump_only=True)


class DataStreamSchema(BaseSchema):
    userIntID = EmqInteger(dump_only=True)
    productID = EmqString(required=True)
    streamName = EmqString(required=True)
    streamType = EmqInteger(required=True)  # 数据流类型
    streamDataType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 数据流数据类型1 json 2 二进制
    dataPoints = EmqList(allow_none=True)  # 二进制数序号和功能点对应关系
    dataPointsOrder = EmqDict(allow_none=True)
    topic = EmqString(required=True, len_max=500)
    detail = EmqString(allow_none=True, len_max=300)
    productType = EmqInteger(load_only=True)  # 产品类型

    @validates_schema
    def validate_stream_type(self, data):
        stream_type = data.get('streamType')
        if stream_type not in range(1, 5):
            raise FormInvalid(field='streamType')
        product_type = data.get('productType')
        # 产品类型为设备，数据流类型只能为 设备数据上报、设备数据下发
        if product_type == 1 and stream_type not in [1, 2]:
            raise FormInvalid(field='streamType')

    @validates_schema
    def validate_data_points(self, data):
        product_type = data.get('productType')
        stream_type = data.get('streamType')
        data_points = data.get('dataPoints')
        # 产品类型为设备，‘dataPoints’ 必填
        if product_type == 1 and not data_points:
            raise FormInvalid(field='dataPoints')
        # 数据流类型是网关数据上报或网关数据下发，‘dataPoints’ 必填
        elif stream_type in [3, 4] and not data_points:
            raise FormInvalid(field='dataPoints')
        elif data_points and any([not isinstance(point_id, int) for point_id in data_points]):
            raise FormInvalid(field='dataPoints')

    @validates('streamName')
    def name_is_exist(self, value):
        if self._validate_obj('streamName', value):
            return
        product_uid = request.get_json().get('productID')
        stream_name = db.session.query(DataStream.streamName) \
            .filter(DataStream.tenantID == g.tenant_uid,
                    DataStream.productID == product_uid,
                    DataStream.streamName == value).first()
        if stream_name:
            raise DataExisted(field='streamName')

    @validates('topic')
    def topic_is_exist(self, value):
        if self._validate_obj('topic', value):
            return
        if not re.match(r"^[0-9A-Za-z_\-/]*$", value):
            raise FormInvalid(field='topic')
        product_uid = request.get_json().get('productID')
        topic = db.session.query(DataStream.topic) \
            .filter(DataStream.tenantID == g.tenant_uid,
                    DataStream.productID == product_uid,
                    DataStream.topic == value).first()
        if topic:
            raise DataExisted(field='topic')

    @pre_load
    def data_processing(self, data):
        """
        将product_int_id转为uid
        将二进制数据流做转换
        """
        product_int_id = data.get('productIntID')
        product_uid = data.get('productID')
        if product_uid and not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        if product_uid:
            pass
        elif product_int_id:
            product_uid = product_id_conversion(product_int_id)
            data['productID'] = product_uid
        elif request.method == 'PUT':
            data.pop('productID', None)
        else:
            raise FormInvalid(field='productIntID')
        data = stream_point_conversion(data)
        product_type = db.session.query(Product.productType) \
            .filter(Product.productID == product_uid) \
            .scalar()
        # 存放 productType, 方便后续验证处理
        data['productType'] = product_type
        stream_type = data.get('streamType')
        stream_data_type = data.get('streamDataType')
        # 产品类型是网关且数据流类型是设备数据上报、设备数据下发，‘dataPoints’ 设为 None
        if product_type == 2 and stream_type in [1, 2]:
            data.pop('dataPoints', None)
            # 由于 ‘dataPoints’ 为 None，因此数据流数据类型只能选择 ‘json’
            if stream_data_type == 2:
                raise FormInvalid(field='streamDataType')
        return data


class UpdateDataStreamSchema(DataStreamSchema):
    streamDataType = EmqInteger(dump_only=True)
    productID = EmqString(dump_only=True)


def product_id_conversion(product_int_id):
    """
    产品int id 转string id
    :param product_int_id: 产品int id
    :return: 产品 string id
    """
    try:
        product_int_id = int(product_int_id)
    except Exception:
        raise FormInvalid(field='productIntID')
    product_uid = db.session.query(Product.productID) \
        .join(User, User.id == Product.userIntID) \
        .filter(Product.id == product_int_id,
                User.tenantID == g.tenant_uid).first()
    if not product_uid:
        raise DataExisted(field='product')
    product_uid = product_uid[0]
    return product_uid


def stream_point_conversion(data):
    """
    对不同类型(json, binary)的数据流功能点做转换
    :param data: 输入数据
    :return: 转换后的数据
    """

    # 对数据类型json和二进制数据分别做处理
    data_type = data.get('streamDataType')
    data_points = data.get('dataPoints')
    data.pop('dataPointsOrder', None)
    if not data_points:
        return data
    if not isinstance(data_points, list):
        raise FormInvalid(field='dataPoints')
    if data_type == 1:
        # 如果是json直接传入不做处理
        data['dataPoints'] = data_points
    elif data_type == 2:
        # 如果是二进制将构建dataPoints 和 dataPointOrder
        try:
            # 验证传入参数是否符合嵌套列表
            data_points_dict = dict(data_points)
        except Exception:
            raise FormInvalid(field='dataPoints')
        data['dataPoints'] = list(data_points_dict.keys())
        data['dataPointsOrder'] = data_points_dict
    else:
        raise FormInvalid(field='streamDataType')
    return data
