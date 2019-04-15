from flask import g, jsonify
from sqlalchemy.exc import IntegrityError

from actor_libs.cache import Cache
from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Action, User
from . import bp
from ..schemas import ActionSchema


@bp.route('/actions')
@auth.login_required
def list_actions():
    query = db.session \
        .query(Action.id, Action.actionName, Action.actionType,
               Action.createAt, User.username.label('createUser')) \
        .join(User, User.id == Action.userIntID)
    records = query.pagination(code_list=['actionType'])
    return jsonify(records)


@bp.route('/actions/<int:action_id>')
@auth.login_required
def view_action(action_id):
    query = db.session.query(Action, User.username.label('createUser')) \
        .join(User, User.id == Action.userIntID) \
        .filter(Action.id == action_id)

    record = query.to_dict()
    record = handle_action_config(record)
    return jsonify(record)


@bp.route('/actions', methods=['POST'])
@auth.login_required
def create_action():
    request_dict = ActionSchema.validate_request()
    action = Action()
    new_action = action.create(request_dict)
    record = new_action.to_dict()
    return jsonify(record), 201


@bp.route('/actions/<int:action_id>', methods=['PUT'])
@auth.login_required
def update_action(action_id):
    action = Action.query \
        .filter(Action.id == action_id) \
        .first_or_404()
    request_dict = ActionSchema.validate_request(obj=action)
    updated_action = action.update(request_dict)
    record = updated_action.to_dict()
    return jsonify(record)


@bp.route('/actions', methods=['DELETE'])
@auth.login_required
def delete_action():
    try:
        ids = get_delete_ids()
        actions = Action.query.filter(Action.id.in_(ids)).many()
        for action in actions:
            if action.business_rules.count() != 0:
                raise ReferencedError()
            db.session.delete(action)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def handle_action_config(record=None):
    cache = Cache()
    dict_code = cache.dict_code
    action_config = record.get('config')
    action_type = record.get('actionType')
    record['actionTypeLabel'] = dict_code.get('actionType').get(action_type) \
        .get(f'{g.language}Label')

    if action_type == 1:
        alert_severity = action_config.get('alertSeverity')
        severity_label = dict_code.get('alertSeverity').get(alert_severity) \
            .get(f'{g.language}Label')
        action_config['alertSeverityLabel'] = severity_label
    elif action_type == 3 and action_config.get('token'):
        ...
    elif action_type == 4:
        ...
    else:
        pass
    return record
