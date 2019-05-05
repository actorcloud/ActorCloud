from flask import jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import DataPoint, DataStream, Client, Product, User
from app.schemas import ProductSchema, UpdateProductSchema
from . import bp


@bp.route('/products')
@auth.login_required
def list_products():
    code_list = ['cloudProtocol', 'productType']
    records = Product.query.pagination(code_list=code_list)
    # Count the number of devices, applications,
    # data points, and data streams of the product
    records_item = records['items']
    records['items'] = records_item_count(records_item)
    return jsonify(records)


@bp.route('/products/<int:product_id>')
@auth.login_required
def view_product(product_id):
    code_list = ['cloudProtocol', 'productType']
    record = Product.query \
        .outerjoin(Client, Client.productID == Product.productID) \
        .join(User, User.id == Product.userIntID) \
        .with_entities(Product, User.username.label('createUser'),
                       func.count(Client.id).label('deviceCount')) \
        .filter(Product.id == product_id) \
        .group_by(Product.id, User.username).to_dict(code_list=code_list)
    return jsonify(record)


@bp.route('/products', methods=['POST'])
@auth.login_required
def create_product():
    request_dict = ProductSchema.validate_request()
    product = Product()
    created_product = product.create(request_dict)
    record = created_product.to_dict()
    return jsonify(record), 201


@bp.route('/products/<int:product_id>', methods=['PUT'])
@auth.login_required
def update_product(product_id):
    product = Product.query.filter(Product.id == product_id).first_or_404()
    request_dict = UpdateProductSchema.validate_request(obj=product)
    updated_product = product.update(request_dict)
    record = updated_product.to_dict()
    return jsonify(record)


@bp.route('/products', methods=['DELETE'])
@auth.login_required
def delete_product():
    delete_ids = get_delete_ids()
    query_results = Product.query \
        .filter(Product.id.in_(delete_ids)) \
        .many(allow_none=False, expect_result=len(delete_ids))

    # check device is included in the delete product
    device_count = db.session.query(func.count(Client.id)) \
        .join(Product, Client.productID == Product.productID) \
        .filter(Product.id.in_(delete_ids)) \
        .scalar()
    if device_count:
        raise ReferencedError(field='device')
    try:
        for product in query_results:
            db.session.delete(product)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def records_item_count(records_item):
    product_dict = {
        item['productID']: item['cloudProtocol']
        for item in records_item
    }
    product_uids = product_dict.keys()
    # Client count
    query = db.session \
        .query(Product.productID, func.count(Client.id)) \
        .outerjoin(Client, Client.productID == Product.productID) \
        .group_by(Product.productID) \
        .filter(Product.productID.in_(product_uids)).all()
    product_device_dict = dict(query)
    # data_point,data_stream or product_item(lwm2m) count
    query = db.session \
        .query(Product.productID, func.count(DataPoint.id)) \
        .outerjoin(DataPoint, DataPoint.productID == Product.productID) \
        .group_by(Product.productID) \
        .filter(Product.productID.in_(product_uids)) \
        .all()
    product_point_dict = dict(query)
    query = db.session \
        .query(Product.productID, func.count(DataStream.id)) \
        .outerjoin(DataStream, DataStream.productID == Product.productID) \
        .group_by(Product.productID) \
        .filter(Product.productID.in_(product_uids)) \
        .all()
    product_stream_dict = dict(query)
    for record in records_item:
        record_product_uid = record['productID']
        record['deviceCount'] = product_device_dict.get(record_product_uid, 0)
        record['dataPointCount'] = product_point_dict.get(record_product_uid, 0)
        record['dataStreamCount'] = product_stream_dict.get(record_product_uid, 0)
    return records_item
