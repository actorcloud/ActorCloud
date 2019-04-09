from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ParameterInvalid, ReferencedError
)
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Product, DataStream, User
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
        .join(User, User.id == DataStream.userIntID) \
        .with_entities(DataStream, User.username.label('createUser')) \
        .filter(DataStream.id == stream_id).to_dict()
    return jsonify(record)


@bp.route('/data_streams/<int:stream_id>/data_points')
@auth.login_required
def view_data_stream_points(stream_id):
    data_stream = DataStream.query \
        .filter(DataStream.id == stream_id).first_or_404()
    stream_points = data_stream.dataPoints.all()
    records = []
    for stream_point in stream_points:
        data_point = stream_point.dataPoint
        records.append(data_point.to_dict())
    return jsonify(records)


@bp.route('/data_streams', methods=['POST'])
@auth.login_required
def create_data_stream():
    request_dict = DataStreamSchema.validate_request()
    data_stream = DataStream()
    created_stream = data_stream.create(request_dict)
    record = created_stream.to_dict()
    return jsonify(record), 201


@bp.route('/data_streams/<int:stream_id>', methods=['PUT'])
@auth.login_required
def update_data_stream(stream_id):
    data_stream = DataStream.query.filter(DataStream.id == stream_id).first_or_404()
    request_dict = UpdateDataStreamSchema.validate_request(obj=data_stream)
    updated_stream = data_stream.update(request_dict)
    record = updated_stream.to_dict()
    return jsonify(record)


@bp.route('/data_streams', methods=['DELETE'])
@auth.login_required
def delete_data_streams():
    delete_ids = get_delete_ids()
    data_streams = DataStream.query \
        .filter(DataStream.id.in_(delete_ids)) \
        .many(allow_none=False, expect_result=len(delete_ids))
    try:
        for data_stream in data_streams:
            db.session.delete(data_stream)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
