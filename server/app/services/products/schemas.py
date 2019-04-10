import re

from flask import g
from marshmallow import validates, pre_load, post_load
from marshmallow.validate import OneOf

from actor_libs.database.orm import db
from actor_libs.errors import DataExisted, FormInvalid, DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger, EmqList, EmqDict
)
from app.models import Product, DataStream, DataPoint


__all__ = [
    'ProductSchema', 'UpdateProductSchema', 'ProductSubSchema',
    'DataPointSchema', 'DataPointUpdateSchema', 'DataStreamSchema',
    'UpdateDataStreamSchema', 'StreamPointsSchema'
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
            .filter_tenant(tenant_uid=g.tenant_uid) \
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


class DataStreamSchema(BaseSchema):
    streamName = EmqString(required=True)
    streamID = EmqInteger(required=True)  # data stream identifier
    streamType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
    topic = EmqString(required=True, len_max=500)
    productID = EmqString(required=True)
    description = EmqString(allow_none=True, len_max=300)
    cloudProtocol = EmqInteger(load_only=True)  # product cloud protocol
    productType = EmqInteger(load_only=True)  # 1: device, 2: gateway

    @validates('streamName')
    def stream_name_is_exist(self, value):
        if self._validate_obj('streamName', value):
            return
        product_uid = self.get_request_data('productID')
        stream_name = db.session.query(DataStream.streamName) \
            .filter(DataStream.productID == product_uid,
                    DataStream.streamName == value).first()
        if stream_name:
            raise DataExisted(field='dataPointName')

    @validates('streamID')
    def stream_id_is_exist(self, value):
        if self._validate_obj('streamID', value):
            return
        product_uid = self.get_request_data('productID')
        stream_name = db.session.query(DataStream.streamID) \
            .filter(DataStream.productID == product_uid,
                    DataStream.streamID == value).first()
        if stream_name:
            raise DataExisted(field='streamID')

    @validates('topic')
    def topic_is_exist(self, value):
        if not value or self._validate_obj('topic', value):
            return
        if not re.match(r"^[0-9A-Za-z_\-/]*$", value):
            raise FormInvalid(field='topic')
        product_uid = self.get_request_data('productID')
        topic = db.session.query(DataStream.topic)\
            .filter(DataStream.productID == product_uid,
                    DataStream.topic == value).first()
        if topic:
            raise DataExisted(field='topic')

    @validates('streamType')
    def validate_stream_type(self, value):
        if self._validate_obj('streamType', value):
            return
        product_type = self.get_request_data('productType')
        if product_type == 1 and value not in (1, 2):
            raise FormInvalid(field='streamType')
        if product_type == 2 and value not in (3, 4):
            raise FormInvalid(field='streamType')

    @pre_load
    def handle_load_data(self, data):
        product_uid: str = data.get('productID')
        if not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        product = Product.query. \
            filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.productID == product_uid).first()
        if not product:
            raise DataNotFound(field='productID')
        data['productID'] = product.productID
        data['cloudProtocol'] = product.cloudProtocol
        data['productType'] = product.productType
        return data


class UpdateDataStreamSchema(DataStreamSchema):
    productID = EmqString(dump_only=True)
    topic = EmqString(dump_only=True, len_max=500)
    dataPoints = EmqList(allow_none=True, load_only=True, list_type=int)

    @post_load
    def handle_data_points(self, data):
        product_uid = self.get_origin_obj('productID')
        data_point_ids = data.get('dataPoints')
        if not data_point_ids:
            return data
        data_points = DataPoint.query \
            .filter(DataPoint.productID == product_uid,
                    DataPoint.id.in_(set(data_point_ids))).all()
        if len(data_points) != len(data_point_ids):
            raise DataNotFound(field='dataPoints')
        data['data_points'] = data_points
        return data


class DataPointSchema(BaseSchema):
    dataPointName = EmqString(required=True)
    dataPointID = EmqString(required=True)
    dataTransType = EmqInteger(required=True)  # message 1: Up, 2: Down, 3 UpAndDown
    pointDataType = EmqInteger(required=True)  # 1:num, 2:str, 3:Boolean, 4:datetime, 5:location
    extendTypeAttr = EmqDict(allow_none=True)  # extension attribute for point data type
    isLocationType = EmqInteger(allow_none=True)  # 1:yes, 2:no
    locationType = EmqInteger(allow_none=True)  # 1: longitude, 2: latitude, 3: altitude
    description = EmqString(allow_none=True, len_max=300)
    enum = EmqList(allow_none=True)  # enum of string or integer
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
    def validate_point_uid(self, value):
        if not value or self._validate_obj('dataPointID', value):
            return

        if not re.match(r"^[0-9A-Za-z_\-]*$", value):
            raise FormInvalid(field='dataPointID')
        product_uid = self.get_request_data('productID')
        data_point_uid = db.session.query(DataPoint.dataPointID) \
            .filter(DataPoint.productID == product_uid,
                    DataPoint.dataPointID == value).first()
        if data_point_uid:
            raise DataExisted(field='dataPointID')

    @pre_load
    def handle_load_data(self, data):
        product_uid: str = data.get('productID')
        if not isinstance(product_uid, str):
            raise FormInvalid(field='productID')
        product = Product.query. \
            filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.productID == product_uid).first()
        if not product:
            raise DataNotFound(field='productID')
        data['productID'] = product.productID
        data['cloudProtocol'] = product.cloudProtocol
        data = handle_extend_type_attr(data)
        return data


class DataPointUpdateSchema(DataPointSchema):
    """功能点更新表单验证"""

    dataPointID = EmqString(dump_only=True)
    productID = EmqString(dump_only=True)


class StreamPointsSchema(BaseSchema):
    dataPoints = EmqList(required=True, list_type=int)

    @post_load
    def convert_data_points(self, data):
        data_point_ids = data.get('dataPoints')
        if data_point_ids:
            data_points = DataPoint.query \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(DataPoint.id.in_(set(data_point_ids))).all()
            if len(data_points) != len(data_point_ids):
                raise DataNotFound(field='dataPoints')
        else:
            data_points = []
        data['dataPoints'] = data_points
        return data


def handle_extend_type_attr(data):
    """ Validate and handle data_point type attribute """

    extend_type_attr: dict = data['extendTypeAttr'] if data.get('extendTypeAttr') else {}
    point_data_type = data.get('pointDataType')
    if point_data_type == 1:
        # number point_data_type
        required_extend_attr = {
            'unitName': None, 'unitSymbol': None,
            'lowerLimit': None, 'upperLimit': None, 'dataStep': None
        }
    else:
        # Extension of other data_point type attributes todo
        required_extend_attr = {}
    required_extend_attr.update(extend_type_attr)
    data['extendTypeAttr'] = required_extend_attr
    return data


