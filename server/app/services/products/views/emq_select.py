from flask import jsonify, request, g

from actor_libs.errors import ParameterInvalid
from app import auth
from app.models import (
    Product, ProductItem, Lwm2mItem,
    Device, DataStream, DataPoint
)
from . import bp


@bp.route('/emq_select/data_points')
@auth.login_required(permission_required=False)
def list_emq_select_data_points():
    query_point = DataPoint.query
    product_int_id = request.args.get('productIntID', type=int)
    product_uid = request.args.get('productID', type=str)
    data_stream_id = request.args.get('dataStreamIntID', type=int)

    if product_int_id and request.args.get('streamDataType', type=int):
        records = product_stream_points(query_point=query_point)
    elif product_uid:
        records = product_rule_points(query_point=query_point)
    elif product_int_id:
        records = product_resource_points(query_point=query_point)
    elif data_stream_id and request.args.get('intID', type=int):
        records = stream_id_points()
    elif data_stream_id:
        records = stream_uid_points()
    else:
        raise ParameterInvalid(field='multiple parameter!')
    return jsonify(records)


@bp.route('/emq_select/data_streams')
@auth.login_required(permission_required=False)
def list_emq_select_data_streams():
    """ 列出某个产品的数据流列表 """

    product_uid = request.args.get('productID', type=str)
    product_id = request.args.get('productIntID', type=int)
    stream_type = request.args.get('streamType', type=int)
    device_id = request.args.get('deviceIntID', type=int)

    query = DataStream.query \
        .join(Product, Product.productID == DataStream.productID)
    if device_id:
        query = query \
            .join(Device, Device.productID == Product.productID) \
            .filter(Device.id == device_id)
    elif product_uid:
        query = query.filter(Product.productID == product_uid)
    elif product_id:
        query = query.filter(Product.id == product_id)
    else:
        raise ParameterInvalid(field='productID or productIntID or deviceIntID')
    data_streams = query.all()
    records = [
        {
            'value': data_stream.id,
            'label': data_stream.streamName,
            'attr': {'streamType': data_stream.streamType}
        }
        for data_stream in data_streams
    ]
    if stream_type:
        records = [{'value': data_stream.id,
                    'label': data_stream.streamName} for data_stream in data_streams
                   if data_stream.streamType == stream_type]
    return jsonify(records)


@bp.route('/emq_select/product/product_items')
@auth.login_required(permission_required=False)
def list_emq_select_product_items():
    """ lwm2m产品 -> 应用模板 """

    product_uid = request.args.get('productID', type=str)
    if not product_uid:
        raise ParameterInvalid(field='productID')

    query_product_items = Lwm2mItem.query \
        .join(ProductItem, ProductItem.itemIntID == Lwm2mItem.id) \
        .filter(Lwm2mItem.itemOperations.isnot(None),
                ProductItem.tenantID == g.tenant_uid,
                ProductItem.productID == product_uid) \
        .with_entities(Lwm2mItem.itemName, Lwm2mItem.itemType,
                       ProductItem.id, Lwm2mItem.itemOperations) \
        .limit(10).all()

    records = [
        {
            'value': product_item.id, 'label': product_item.itemName,
            'attr': {
                'itemOperations': product_item.itemOperations,
                'itemType': product_item.itemType
            }
        }
        for product_item in query_product_items
    ]
    return jsonify(records)


def product_stream_points(query_point):
    """
    新建数据流时返回该产品下的所有功能点
    :param query_point: 基础查询功能点
    :return: (dataIntID: dataPointName)
    """

    product_id = request.args.get('productIntID', type=int)
    stream_data_type = request.args.get('streamDataType', type=int)
    stream_type = request.args.get('streamType', type=int)
    if stream_type not in [1, 2, 3, 4]:
        raise ParameterInvalid(field='streamType')
    data_trans_type = 1 if stream_type in [1, 3] else 2
    # 新建数据流下功能点
    query_point = query_point.join(Product, Product.productID == DataPoint.productID) \
        .filter(Product.id == product_id, DataPoint.dataTransType.in_([data_trans_type, 3]))
    # 依据数据流不同的数据格式(1 JSON 2 二进制)返回不同的功能点(1~10 JSON 11~20 二进制)
    if stream_data_type == 1:
        query_point = query_point.filter(DataPoint.pointDataType.between(1, 10))
    elif stream_data_type == 2:
        query_point = query_point.filter(DataPoint.pointDataType.between(11, 20))
    else:
        raise ParameterInvalid(field='streamDataType')
    data_points = query_point.all()
    records = [{'value': data_point.id,
                'label': data_point.dataPointName} for data_point in data_points]
    return records


def product_rule_points(query_point):
    """
    新建业务规则时 返回该产品下的所有功能点
    :param query_point: 基础查询功能点
    :return: (dataPointID: dataPointName)
    """

    product_uid = request.args.get('productID', type=str)
    data_points = query_point.filter(DataPoint.productID == product_uid).all()
    records = [{'value': data_point.dataPointID,
                'label': data_point.dataPointName,
                'attr': {
                    'enum': data_point.enum,
                    'pointDataType': data_point.pointDataType,
                    'faultValue': data_point.faultValue
                }} for data_point in data_points]
    return records


def product_resource_points(query_point):
    """
    新建产品资源时，返回该产品下的所有功能点
    :param query_point: 基础查询功能点
    :return: (dataPointIntID: dataPointName)
    """

    product_id = request.args.get('productIntID', type=int)
    product = Product.query.filter(Product.id == product_id).first()
    data_points = query_point.filter(DataPoint.productID == product.productID).all()
    records = [{'value': data_point.id,
                'label': data_point.dataPointName} for data_point in data_points]
    return records


def stream_uid_points():
    """
    返回指定id数据流下的所有功能点
    :return: (dataPointID: dataPointName)
    """

    data_stream_id = request.args.get('dataStreamIntID', type=int)
    data_stream = DataStream.query \
        .filter(DataStream.id == data_stream_id, DataStream.tenantID == g.tenant_uid) \
        .first_or_404()

    stream_points = data_stream.dataPoints
    records = [
        {'value': stream_point.dataPoint.dataPointID,
         'label': stream_point.dataPoint.dataPointName,
         'attr': {
             'enum': stream_point.dataPoint.enum,
             'pointDataType': stream_point.dataPoint.pointDataType,
             'faultValue': stream_point.dataPoint.faultValue
         }} for stream_point in stream_points]
    return records


def stream_id_points():
    """
    返回指定id数据流下的所有功能点
    :return: (dataPointID: dataPointName)
    """

    data_stream_id = request.args.get('dataStreamIntID', type=int)
    data_stream = DataStream.query \
        .filter(DataStream.id == data_stream_id, DataStream.tenantID == g.tenant_uid) \
        .first_or_404()

    stream_points = data_stream.dataPoints
    records = [
        {'value': stream_point.dataPoint.id,
         'label': stream_point.dataPoint.dataPointName,
         'attr': {
             'enum': stream_point.dataPoint.enum,
             'pointDataType': stream_point.dataPoint.pointDataType,
             'dataTransType': stream_point.dataPoint.dataTransType
         }
         } for stream_point in stream_points
    ]
    return records
