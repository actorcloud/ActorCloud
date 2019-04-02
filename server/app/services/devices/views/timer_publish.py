from flask import jsonify, request, g
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import literal

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid, ReferencedError
from actor_libs.schemas.publish_schema import TimerPublishSchema
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import TimerPublish, User, Client, Group
from . import bp


@bp.route('/timer_publish', methods=['GET'])
@auth.login_required
def list_timer_publish():
    device_uid = request.args.get('deviceID', type=str)
    group_uid = request.args.get('groupID', type=str)
    if device_uid:
        query = get_client_timer_publish(device_uid=device_uid)
    elif group_uid:
        query = get_group_timer_publish(group_uid=group_uid)
    else:
        query = db.session \
            .query(TimerPublish, User.username,
                   Client.deviceName, Client.deviceID,
                   Group.id.label('groupIntID'), Group.groupName) \
            .outerjoin(Client, Client.id == TimerPublish.deviceIntID) \
            .outerjoin(Group, Group.groupID == TimerPublish.groupID) \
            .join(User, User.id == TimerPublish.userIntID)

    code_list = ['controlType', 'taskStatus', 'timerType', 'publishType']
    record = query.pagination(code_list=code_list)
    return jsonify(record)


@bp.route('/timer_publish', methods=['POST'])
@auth.login_required
def create_timer_publish():
    request_dict = TimerPublishSchema.validate_request()
    timer_publish = TimerPublish()
    new_timer_publish = timer_publish.create(request_dict)
    record = new_timer_publish.to_dict()
    return jsonify(record)


@bp.route('/timer_publish', methods=['DELETE'])
@auth.login_required
def delete_timer_publish():
    delete_ids = get_delete_ids()

    query_results = TimerPublish.query \
        .join(User, User.id == TimerPublish.userIntID) \
        .filter(User.tenantID == g.tenant_uid,
                TimerPublish.id.in_(delete_ids)) \
        .all()
    if len(delete_ids) != len(query_results):
        raise ParameterInvalid(field='ids')
    try:
        for query_result in query_results:
            db.session.delete(query_result)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def get_client_timer_publish(device_uid=None):
    client = Client.query \
        .with_entities(Client.id, Client.deviceName, Client.deviceID) \
        .filter(Client.deviceID == device_uid) \
        .first_or_404()

    query = db.session \
        .query(TimerPublish, User.username,
               literal(client.deviceID).label("deviceID"),
               literal(client.deviceName).label("deviceName")) \
        .join(User, User.id == TimerPublish.userIntID) \
        .filter(TimerPublish.publishType == 1,
                TimerPublish.deviceIntID == client.id)
    return query


def get_group_timer_publish(group_uid=None):
    group = Group.query \
        .with_entities(Group.groupID, Group.groupName, Group.id) \
        .filter(Group.groupID == group_uid) \
        .first_or_404()
    query = db.session \
        .query(TimerPublish, User.username,
               literal(group.id).label("groupIntID"),
               literal(group.groupName).label("groupName")) \
        .join(User, User.id == TimerPublish.userIntID) \
        .filter(TimerPublish.publishType == 2,
                TimerPublish.groupID == group.groupID)
    return query
