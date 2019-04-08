from flask import g, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import DataExisted, ReferencedError, ResourceLimited
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    Application, ApplicationProduct, DataPoint, DataStream, Client,
    MqttSub, Product, ProductGroupSub, ProductItem, User
)
from app.schemas import ProductSchema, UpdateProductSchema, ProductSubSchema
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
    request_dict['userIntID'] = g.user_id
    product = Product()
    created_product = product.create(request_dict, commit=False)

    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        created_product.applications.append(application)
    db.session.commit()
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


@bp.route('/products/<int:product_id>/subscriptions')
@auth.login_required
def list_product_subs(product_id):
    product = Product.query.with_entities(Product.id) \
        .filter(Product.id == product_id).first_or_404()

    sub_query = ProductGroupSub.query \
        .filter(ProductGroupSub.productIntID == product.id)
    records = sub_query.pagination()
    return jsonify(records)


@bp.route('/products/<int:product_id>/subscriptions', methods=['POST'])
@auth.login_required
def create_product_sub(product_id):
    request_dict = ProductSubSchema.validate_request()
    product = Product.query.filter(Product.id == product_id).first_or_404()

    topic = request_dict.get('topic')
    if product.cloudProtocol != 1:
        raise ResourceLimited(field='cloudProtocol')
    sub_topic = db.session.query(ProductGroupSub.topic) \
        .join(Product, Product.id == ProductGroupSub.productIntID) \
        .filter(Product.id == product_id,
                ProductGroupSub.topic == topic) \
        .first()
    if sub_topic:
        raise DataExisted(field='topic')
    if product.devices.count() > 1000:
        raise ResourceLimited(field='devices')

    product_sub = ProductGroupSub(topic=topic, productIntID=product_id)
    db.session.add(product_sub)
    sub_client_dict = {}
    for device in product.devices:
        client_uid = ':'.join(
            [g.tenant_uid, device.productID, device.deviceID]
        )
        sub_client_dict[client_uid] = device.id
    devices_sub_sum = db.session \
        .query(MqttSub.clientID, func.count(MqttSub.id)) \
        .filter(MqttSub.clientID.in_(sub_client_dict.keys())) \
        .group_by(MqttSub.clientID) \
        .all()
    devices_sub_sum_dict = dict(devices_sub_sum)
    devices_sub_exist = db.session.query(MqttSub.clientID) \
        .filter(MqttSub.clientID.in_(sub_client_dict.keys()),
                MqttSub.topic == topic) \
        .all()

    for client_uid, device_id in sub_client_dict.items():
        if (client_uid,) in devices_sub_exist:
            continue
        if devices_sub_sum_dict.get(client_uid, 0) >= 10:
            continue
        mqtt_sub = MqttSub(
            clientID=client_uid, topic=topic,
            qos=request_dict.get('qos', 1), deviceIntID=device_id
        )
        db.session.add(mqtt_sub)
    db.session.commit()
    record = product_sub.to_dict()
    return jsonify(record), 201


@bp.route('/products/<int:product_id>/subscriptions', methods=['DELETE'])
@auth.login_required
def delete_product_sub(product_id):
    delete_ids = get_delete_ids()
    product_subs = db.session.query(ProductGroupSub) \
        .filter(ProductGroupSub.id.in_(delete_ids),
                ProductGroupSub.productIntID == product_id) \
        .all()
    product = Product.query.filter(Product.id == product_id).first_or_404()
    device_ids = [device.id for device in product.devices]
    try:
        delete_topic = []
        for product_sub in product_subs:
            delete_topic.append(product_sub.topic)
            db.session.delete(product_sub)
        query_mqtt_sub = MqttSub.query \
            .filter(MqttSub.deviceIntID.in_(device_ids),
                    MqttSub.topic.in_(delete_topic)) \
            .all()
        for mqtt_sub in query_mqtt_sub:
            db.session.delete(mqtt_sub)
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
    # application count
    query = db.session \
        .query(Product.productID,
               func.count(ApplicationProduct.c.applicationIntID)) \
        .join(ApplicationProduct) \
        .group_by(Product.productID) \
        .filter(Product.productID.in_(product_uids)) \
        .all()
    product_app_dict = dict(query)
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
    query = db.session \
        .query(Product.productID, func.count(ProductItem.id)) \
        .outerjoin(ProductItem, ProductItem.productID == Product.productID) \
        .group_by(Product.productID) \
        .filter(Product.cloudProtocol == 3,
                Product.productID.in_(product_uids)) \
        .all()
    product_item_dict = dict(query)
    for record in records_item:
        record_product_uid = record['productID']
        record['deviceCount'] = product_device_dict.get(record_product_uid, 0)
        record['appCount'] = product_app_dict.get(record_product_uid, 0)
        if product_dict.get(record_product_uid) == 3:
            record['itemCount'] = product_item_dict.get(record_product_uid, 0)
        else:
            record['dataPointCount'] = product_point_dict.get(record_product_uid, 0)
            record['dataStreamCount'] = product_stream_dict.get(record_product_uid, 0)
    return records_item
