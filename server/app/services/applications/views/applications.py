from flask import g, jsonify, request
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Application, Product, Role, User
from app.schemas import ApplicationSchema
from . import bp


@bp.route('/applications')
@auth.login_required
def list_applications():
    query = Application.query
    product_id = request.args.get('productID')
    if product_id:
        query = query.filter(Application.products.any(Product.productID == product_id))
    records = query.pagination()
    return jsonify(records)


@bp.route('/applications/<int:application_id>')
@auth.login_required
def view_application(application_id):
    application, role_name, username = Application.query \
        .join(User, User.id == Application.userIntID) \
        .join(Role, Role.id == Application.roleIntID) \
        .with_entities(Application, Role.roleName, User.username) \
        .filter(Application.id == application_id) \
        .first_or_404()
    # get products of the application
    product_uids = []
    product_index = []
    for product in application.products:
        product_index.append({'value': product.id, 'label': product.productName})
        product_uids.append(product.productID)
    # dumps query
    record = application.to_dict()
    record['products'] = product_uids
    record['productIndex'] = product_index
    record['createUser'] = username
    record['roleName'] = role_name
    return jsonify(record)


@bp.route('/applications', methods=['POST'])
@auth.login_required
def create_application():
    request_dict = ApplicationSchema.validate_request()
    request_dict['userIntID'] = g.user_id
    application = Application()
    created_app = application.create(request_dict)
    record = created_app.to_dict()
    return jsonify(record), 201


@bp.route('/applications/<int:application_id>', methods=['PUT'])
@auth.login_required
def update_application(application_id):
    application = Application.query \
        .filter(Application.id == application_id).first_or_404()
    request_dict = ApplicationSchema.validate_request(obj=application)
    # update app
    updated_app = application.update(request_dict)
    record = updated_app.to_dict()
    return jsonify(record)


@bp.route('/applications', methods=['DELETE'])
@auth.login_required
def delete_application():
    app_ids = get_delete_ids()
    applications = Application.query \
        .filter(Application.id.in_(app_ids)).many(allow_none=False)
    try:
        for app in applications:
            app.delete()
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
