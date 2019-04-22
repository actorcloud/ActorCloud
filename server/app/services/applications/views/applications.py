from flask import jsonify
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Application, ApplicationGroup, Group, Role, User
from app.schemas import ApplicationSchema
from . import bp


@bp.route('/applications')
@auth.login_required
def list_applications():
    records = Application.query.pagination()
    return jsonify(records)


@bp.route('/applications/<int:application_id>')
@auth.login_required
def view_application(application_id):
    record = Application.query \
        .join(Role, Role.id == Application.roleIntID)\
        .join(User, User.id == Application.userIntID) \
        .with_entities(Application, Role.roleName, User.username) \
        .filter(Application.id == application_id).to_dict()
    # get groups of the application
    groups = Group.query \
        .join(ApplicationGroup, ApplicationGroup.c.groupID == Group.groupID) \
        .filter(ApplicationGroup.c.applicationIntID == application_id).all()
    groups_uid = []
    groups_index = []
    for group in groups:
        groups_uid.append(group.groupID)
        groups_index.append({'value': group.id, 'label': group.groupName})
    record['groups'] = groups_uid
    record['groupsIndex'] = groups_index
    return jsonify(record)


@bp.route('/applications', methods=['POST'])
@auth.login_required
def create_application():
    request_dict = ApplicationSchema.validate_request()
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
    updated_app = application.update(request_dict)
    record = updated_app.to_dict()
    return jsonify(record)


@bp.route('/applications', methods=['DELETE'])
@auth.login_required
def delete_application():
    app_ids = get_delete_ids()
    applications = Application.query \
        .filter(Application.id.in_(app_ids)) \
        .many(allow_none=False, expect_result=len(app_ids))
    try:
        for app in applications:
            app.delete()
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
