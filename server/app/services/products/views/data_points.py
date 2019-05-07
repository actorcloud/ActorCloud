from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ParameterInvalid, ReferencedError
)
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    User, Product, DataPoint
)
from . import bp
from ..schemas import DataPointSchema, DataPointUpdateSchema


@bp.route('/data_points')
@auth.login_required
def list_data_points():
    code_list = ['dataTransType', 'pointDataType']
    product_uid = request.args.get('productID', type=str)
    if not product_uid:
        raise ParameterInvalid(field='productID')

    query = DataPoint.query \
        .join(Product, DataPoint.productID == Product.productID) \
        .filter(Product.productID == product_uid) \
        .with_entities(DataPoint, Product.productName)
    records = query.pagination(code_list=code_list)
    return jsonify(records)


@bp.route('/data_points/<int:point_id>')
@auth.login_required
def view_data_point(point_id):
    record = DataPoint.query \
        .join(User, User.id == DataPoint.userIntID) \
        .with_entities(DataPoint, User.username.label('createUser')) \
        .filter(DataPoint.id == point_id).to_dict()
    return jsonify(record)


@bp.route('/data_points', methods=['POST'])
@auth.login_required
def create_data_point():
    request_dict = DataPointSchema.validate_request()
    data_point = DataPoint()
    created_point = data_point.create(request_dict)
    record = created_point.to_dict()
    return jsonify(record), 201


@bp.route('/data_points/<int:point_id>', methods=['PUT'])
@auth.login_required
def update_data_point(point_id):
    data_point = DataPoint.query.filter(DataPoint.id == point_id).first_or_404()
    request_dict = DataPointUpdateSchema.validate_request(obj=data_point)
    updated_record = data_point.update(request_dict)
    record = updated_record.to_dict()
    return jsonify(record)


@bp.route('/data_points', methods=['DELETE'])
@auth.login_required
def delete_data_points():
    delete_ids = get_delete_ids()
    data_points = DataPoint.query \
        .filter(DataPoint.id.in_(delete_ids)) \
        .many(allow_none=False, expect_result=len(delete_ids))
    try:
        for data_point in data_points:
            if data_point.dataStreams.count() > 0:
                raise ReferencedError(field='dataStream')
            db.session.delete(data_point)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204

