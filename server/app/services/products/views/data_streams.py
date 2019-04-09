from flask import jsonify, request, g
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ParameterInvalid, ReferencedError, FormInvalid, DataNotFound
)
from app import auth
from app.models import Product, DataStream, DataPoint, StreamPoint
from app.schemas import DataStreamSchema, UpdateDataStreamSchema
from . import bp


@bp.route('/data_streams')
@auth.login_required
def list_data_streams():
    code_list = ['streamType', 'streamDataType']
    product_uid = request.args.get('productID', type=str)
    if not product_uid:
        raise ParameterInvalid(field='productID')

    query = DataStream.query \
        .join(Product, DataStream.productID == Product.productID) \
        .filter(Product.productID == product_uid) \
        .with_entities(DataStream, Product.productName)
    records = query.pagination(code_list=code_list)
    return jsonify(records)


@bp.route('/data_streams/<int:stream_id>')
@auth.login_required
def view_data_stream(stream_id):
    record = DataStream.query \
        .join(User, User.id == DataPoint.userIntID) \
        .with_entities(DataPoint, User.username.label('createUser')) \
        .filter(DataStream.id == stream_id).to_dict()
    return jsonify(record)


@bp.route('/data_streams/<int:stream_id>/data_points')
@auth.login_required
def view_data_stream_points(stream_id):
    data_stream = DataStream.query.filter(DataStream.id == stream_id) \
        .first_or_404()
    stream_points = data_stream.dataPoints
    records = []
    for stream_point in stream_points:
        data_point = stream_point.dataPoint
        records.append(data_point.to_dict())
    return jsonify(records)


@bp.route('/data_streams', methods=['POST'])
@auth.login_required
def create_data_stream():
    request_dict = DataStreamSchema.validate_request()
    data_type = request_dict.get('streamDataType')
    point_ids = request_dict.pop('dataPoints', [])
    points_order_dict = request_dict.pop('dataPointsOrder', None)
    product_uid = request_dict.get('productID')
    stream_type = request_dict.get('streamType')
    # 根据数据流上报下发类型，过滤功能点类型
    data_trans_type = 1 if stream_type in [1, 3] else 2

    # 查询传入功能点id是否合法
    data_points = DataPoint.query \
        .filter(DataPoint.productID == product_uid, DataPoint.tenantID == g.tenant_uid,
                DataPoint.dataTransType.in_([data_trans_type, 3])) \
        .filter(DataPoint.id.in_(point_ids)).all()
    if len(point_ids) != len(data_points):
        raise DataNotFound(field='URL')

    data_streams = DataStream(
        streamName=request_dict.get('streamName'),
        streamType=stream_type,
        topic=request_dict.get('topic'), detail=request_dict.get('detail'),
        streamDataType=data_type, productID=product_uid, userIntID=g.user_id, tenantID=g.tenant_uid
    )
    for data_point in data_points:
        if not data_point:
            continue
        stream_point = StreamPoint()
        # 如果是二进制，则需要新增二进制序号
        if data_type == 2 and points_order_dict:
            point_order = points_order_dict.get(data_point.id)
            if not isinstance(point_order, int):
                db.session.close()
                raise FormInvalid(field='dataPointOrder')
            stream_point.binaryPointOrder = point_order
        # 数据流添加功能点
        stream_point.dataPoint = data_point
        data_streams.dataPoints.append(stream_point)
    db.session.add(data_streams)
    db.session.commit()
    record = data_streams.to_dict()
    record['dataPoints'] = point_ids
    return jsonify(record), 201


@bp.route('/data_streams/<int:stream_id>', methods=['PUT'])
@auth.login_required
def update_data_stream(stream_id):
    data_stream = DataStream.query.filter(DataStream.id == stream_id).first_or_404()
    request_dict = UpdateDataStreamSchema.validate_request(obj=data_stream)
    point_ids = request_dict.pop('dataPoints')
    points_order_dict = request_dict.pop('dataPointsOrder', None)
    # 必须保证如果为二进制就必须要有二进制序号
    if data_stream.streamDataType == 2 and not points_order_dict:
        raise FormInvalid(field='dataPoints')
    input_stream_points = DataPoint.query \
        .filter(DataPoint.productID == data_stream.productID, DataPoint.tenantID == g.tenant_uid) \
        .filter(DataPoint.id.in_(point_ids)).all()
    if len(point_ids) != len(input_stream_points):
        raise DataNotFound(field='URL')
    # 更新数据流
    for key, value in request_dict.items():
        if hasattr(data_stream, key):
            setattr(data_stream, key, value)
    data_stream = update_stream_points(
        data_stream=data_stream, order_dict=points_order_dict,
        input_stream_points=input_stream_points
    )
    record = data_stream.to_dict()
    record['dataPoints'] = point_ids
    return jsonify(record)


@bp.route('/data_streams', methods=['DELETE'])
@auth.login_required
def delete_data_streams(query_results):
    delete_ids = get_delete_ids()
    data_streams = DataStream.query \
        .filter(DataStream.id.in_(delete_ids)) \
        .many(allow_none=False, expect_result=len(delete_ids))
    try:
        #  association object delete 级联删除有问题 todo
        for data_stream in data_streams:
            delete_stream_point = StreamPoint.query \
                .filter(StreamPoint.dataStreamIntID == data_stream.id).all()
            for stream_point in delete_stream_point:
                db.session.delete(stream_point)
            db.session.delete(data_stream)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def update_stream_points(data_stream, input_stream_points, order_dict):
    origin_stream_points = [i.dataPoint for i in data_stream.dataPoints]
    add_data_points = set(input_stream_points).difference(set(origin_stream_points))
    delete_data_points = set(origin_stream_points).difference(set(input_stream_points))
    delete_point_ids = [i.id for i in delete_data_points]
    data_type = data_stream.streamDataType

    # 删除功能点
    if delete_data_points:
        delete_stream_point = StreamPoint.query \
            .filter(and_(StreamPoint.dataStreamIntID == data_stream.id,
                         StreamPoint.dataPointIntID.in_(delete_point_ids))).all()
        for stream_point in delete_stream_point:
            db.session.delete(stream_point)

    if data_type == 2:
        # 更新二进制顺序
        for stream_point in data_stream.dataPoints:
            point_id = stream_point.dataPointIntID
            point_order = order_dict.get(point_id)
            if not isinstance(point_order, int) and point_id not in delete_point_ids:
                db.session.close()
                raise FormInvalid(field='dataPointOrder')
            if stream_point.binaryPointOrder != point_order:
                stream_point.binaryPointOrder = point_order

    # 新增功能点
    if add_data_points:
        for data_point in add_data_points:
            stream_point = StreamPoint()
            if data_type == 2 and order_dict:
                point_order = order_dict.get(data_point.id)
                if not isinstance(point_order, int):
                    db.session.close()
                    raise FormInvalid(field='dataPointOrder')
                stream_point.binaryPointOrder = point_order
            stream_point.dataPoint = data_point
            data_stream.dataPoints.append(stream_point)
    db.session.commit()
    return data_stream
