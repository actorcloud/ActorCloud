from flask import jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Client, Group, GroupDevice, User
from app.schemas import GroupSchema, GroupDeviceSchema
from . import bp


@bp.route('/groups')
@auth.login_required
def list_groups():
    query = Group.query.outerjoin(GroupDevice) \
        .with_entities(Group, func.count(GroupDevice.c.clientIntID).label('clientCount')) \
        .group_by(Group)

    records = query.pagination()
    return jsonify(records)


@bp.route('/groups/<int:group_id>')
@auth.login_required
def view_group(group_id):
    query = Group.query \
        .join(User, User.id == Group.userIntID) \
        .with_entities(Group, User.username) \
        .filter(Group.id == group_id)
    record = query.to_dict()
    return jsonify(record)


@bp.route('/groups', methods=['POST'])
@auth.login_required
def create_group():
    request_dict = GroupSchema.validate_request()
    group = Group()
    new_group = group.create(request_dict)
    record = new_group.to_dict()
    return jsonify(record), 201


@bp.route('/groups/<int:group_id>', methods=['PUT'])
@auth.login_required
def update_group(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    request_dict = GroupSchema.validate_request(obj=group)
    updated_group = group.update(request_dict)
    record = updated_group.to_dict()
    return jsonify(record)


@bp.route('/groups', methods=['DELETE'])
@auth.login_required
def delete_group():
    delete_ids = get_delete_ids()
    query_results = Group.query.filter(Group.id.in_(delete_ids)).many()
    try:
        for group in query_results:
            device_count = db.session.query(func.count(GroupDevice.c.clientIntID)) \
                .filter(GroupDevice.c.groupID == group.groupID).scalar()
            if device_count > 0:
                raise ReferencedError(field='device')
            db.session.delete(group)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/groups/<int:group_id>/devices')
@auth.login_required
def view_group_clients(group_id):
    group = Group.query.with_entities(Group.groupID) \
        .filter(Group.id == group_id).first_or_404()
    query = group.devices
    records = query.pagination(code_list=['deviceTypeLabel'])
    return jsonify(records)


@bp.route('/groups/<int:group_id>/devices', methods=['POST'])
@auth.login_required
def add_group_clients(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    request_dict = GroupDeviceSchema.validate_request()
    clients = request_dict['clients']
    group.clients.extend(clients)
    group.update()
    return '', 201


@bp.route('/groups/<int:group_id>/devices', methods=['DELETE'])
@auth.login_required
def delete_group_devices(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    delete_ids = get_delete_ids()
    clients = GroupDevice.query \
        .join(Client, Client.id == GroupDevice.c.clientIntID) \
        .filter(GroupDevice.c.groupID == group.groupID,
                Client.id.in_(delete_ids)).all()
    for client in clients:
        group.clients.remove(client)
    group.update()
    return '', 204
