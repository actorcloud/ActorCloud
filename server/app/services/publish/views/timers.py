from flask import jsonify, request, g
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid, ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import TimerPublish, User, Client
from app.schemas import TimerPublishSchema
from . import bp


@bp.route('/timer_publish', methods=['GET'])
@auth.login_required
def list_timer_publish():
    query = TimerPublish.query \
        .join(Client, Client.id == TimerPublish.clientIntID) \
        .join(User, User.id == TimerPublish.userIntID) \
        .with_entities(TimerPublish,
                       User.username.label('createUser'),
                       Client.deviceName, Client.clientType)
    device_uid = request.args.get('deviceID', type=str)
    if device_uid:
        # get client time publish list
        query = query.filter(Client.deviceID == device_uid)
    code_list = ['controlType', 'taskStatus', 'timerType']
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
