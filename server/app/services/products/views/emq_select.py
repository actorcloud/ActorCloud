from flask import request, jsonify

from actor_libs.errors import ParameterInvalid
from app import auth
from app.models import Product, DataStream, DataPoint, StreamPoint
from . import bp


@bp.route('/emq_select/products')
@auth.login_required(permission_required=False)
def list_emq_select_products():
    product_type = request.args.get('productType', type=int)
    query = Product.query
    if product_type == 1:
        query = query.filter(Product.productType == 1)
    elif product_type == 2:
        query = query.filter(Product.productType == 2)
    attrs = ['productIntID', 'productType', 'cloudProtocol', 'gatewayProtocol']
    records = query \
        .with_entities(Product.productID.label('value'),
                       Product.productName.label('label'),
                       Product.id.label('productIntID'),
                       Product.productType,
                       Product.cloudProtocol,
                       Product.gatewayProtocol) \
        .select_options(attrs=attrs)
    return jsonify(records)


@bp.route('/emq_select/data_streams')
@auth.login_required(permission_required=False)
def list_emq_select_data_streams():
    product_uid = request.args.get('productID', type=str)
    query = DataStream.query
    if product_uid:
        query = query.filter(DataStream.productID == product_uid)
    records = query \
        .with_entities(DataStream.id.label('value'),
                       DataStream.streamName.label('label'),
                       DataStream.streamType,
                       DataStream.productID,
                       DataStream.topic,
                       DataStream.streamID) \
        .select_options(attrs=['streamType', 'streamID', 'productID'])
    return jsonify(records)


@bp.route('/emq_select/data_points')
@auth.login_required(permission_required=False)
def list_emq_select_data_points():
    product_uid = request.args.get('productID', type=str)
    data_stream_id = request.args.get('dataStreamIntID', type=int)
    query = DataPoint.query
    if product_uid:
        query = query.filter(DataPoint.productID == product_uid)
    if data_stream_id:
        query = query \
            .join(StreamPoint, StreamPoint.c.dataPointIntID == DataPoint.id)\
            .filter(StreamPoint.c.dataStreamIntID == data_stream_id)
    attrs = ['dataPointID', 'dataTransType', 'pointDataType', 'productID']
    records = query \
        .with_entities(DataPoint.id.label('value'),
                       DataPoint.dataPointName.label('label'),
                       DataPoint.dataPointID,
                       DataPoint.dataTransType,
                       DataPoint.pointDataType,
                       DataPoint.productID) \
        .select_options(attrs=attrs)
    return jsonify(records)


@bp.route('/emq_select/stream_datapoints')
@auth.login_required(permission_required=False)
def list_emq_select_stream_points():
    """ Return all data_points under data_stream """

    product_uid = request.args.get('productID', type=str)
    query = DataStream.query
    if product_uid:
        query = query.filter(DataStream.productID == product_uid)
    streams_tree = []
    data_streams = query.many()
    for data_stream in data_streams:
        data_points = []
        for data_point in data_stream.dataPoints:
            select_option = {
                'label': data_point.dataPointName,
                'value': data_point.dataPointID
            }
            data_points.append(select_option)
        streams_tree.append({
            'label': data_stream.streamName,
            'value': data_stream.streamID,
            'children': data_points
        })
    return jsonify(streams_tree)


@bp.route('/emq_select/topics')
@auth.login_required(permission_required=False)
def list_emq_select_topics():
    product_uid = request.args.get('productID', type=str)
    if not product_uid:
        raise ParameterInvalid(field='productID')
    product = Product.query.filter_by(productID=product_uid).first_or_404()
    if product.cloudProtocol == 3:
        record = [
            {
                'key': 'ad/#',
                'value': 'ad/#'
            }]
    else:
        topics = DataStream.query \
            .with_entities(DataStream.topic) \
            .filter(DataStream.productID == product_uid) \
            .many()
        record = [
            {
                'key': topic.topic,
                'value': topic.topic
            }
            for topic in topics
        ]

    return jsonify(record)
