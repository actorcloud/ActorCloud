import json
from typing import AnyStr

from flask import jsonify, request, current_app
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.emqx.publish.protocol import PROTOCOL_PUBLISH_JSON_FUNC
from actor_libs.errors import (
    ReferencedError, FormInvalid, InternalError
)
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.utils import get_delete_ids, generate_uuid
from app import auth
from app.models import (
    User, Rule, Action, RuleAction
)
from . import bp
from ..schemas import (
    AlertActionSchema, EmailActionSchema, RuleSchema, UpdateRuleSchema, PublishActionSchema,
    MqttActionSchema
)


@bp.route('/rules')
@auth.login_required
def list_rules():
    query = Rule.query \
        .with_entities(Rule.id, Rule.ruleName, Rule.sql,
                       Rule.enable, Rule.remark)

    records = query.pagination()
    return jsonify(records)


@bp.route('/rules', methods=['POST'])
@auth.login_required
def create_rule():
    request_dict = RuleSchema.validate_request()
    rule = Rule()
    new_rule = rule.create(request_dict, commit=False)

    action_ids = request.get_json().get('actions')
    if not isinstance(action_ids, list):
        raise FormInvalid(field='actions')
    actions = Action.query \
        .filter(Action.id.in_(action_ids)) \
        .many()
    for action in actions:
        new_rule.actions.append(action)

    rule_json = get_rule_json(new_rule)
    url = f"{current_app.config.get('STREAM_RULE_URL')}/"
    stream_rule_http('post', url=url, json=rule_json)
    db.session.commit()
    record = new_rule.to_dict()
    return jsonify(record), 201


@bp.route('/rules/<int:rule_id>')
@auth.login_required
def view_rule(rule_id):
    record = Rule.query \
        .join(User, User.id == Rule.userIntID) \
        .with_entities(Rule, User.username.label('createUser')) \
        .filter(Rule.id == rule_id) \
        .to_dict()

    actions = db.session.query(Action.actionName) \
        .join(RuleAction) \
        .filter(RuleAction.c.ruleIntID == rule_id) \
        .all()
    action_names = [action.actionName for action in actions]
    record['actionNames'] = action_names
    return jsonify(record)


@bp.route('/rules/<int:rule_id>', methods=['PUT'])
@auth.login_required
def update_rule(rule_id):
    rule = Rule.query \
        .filter(Rule.id == rule_id) \
        .first_or_404()
    old_enable = rule.enable
    request_dict = UpdateRuleSchema.validate_request(obj=rule)
    updated_rule = rule.update(request_dict, commit=False)

    action_ids = request.get_json().get('actions')
    if action_ids:
        update_actions = Action.query \
            .filter(Action.id.in_(action_ids)) \
            .many()
        updated_rule.actions = update_actions
    rule_json = get_rule_json(updated_rule)
    url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule_id}"
    stream_rule_http('put', url=url, json=rule_json)
    changed = old_enable != updated_rule.enable
    if changed:
        switch = 'start' if updated_rule.enable else 'stop'
        switch_url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule_id}/{switch}"
        stream_rule_http('put', url=switch_url)
    db.session.commit()
    record = updated_rule.to_dict()
    return jsonify(record)


@bp.route('/rules', methods=['DELETE'])
@auth.login_required
def delete_rule():
    try:
        ids = get_delete_ids()
        rules = Rule.query \
            .filter(Rule.id.in_(ids)) \
            .many()
        for rule in rules:
            db.session.delete(rule)
            url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule.id}"
            stream_rule_http('delete', url=url)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def get_rule_json(rule):
    rule_actions = []
    for action in rule.actions:
        if action.actionType == 1:
            alert_dict = AlertActionSchema().dump(action.config).data
            action_config = {
                'webhook': {
                    **alert_dict,
                    'url': current_app.config.get('CURRENT_ALERT_URL'),
                    'ruleIntID': rule.id

                }
            }
            rule_actions.append(action_config)
        elif action.actionType == 2:
            email_dict = EmailActionSchema().dump(action.config).data
            action_config = {
                'mail': email_dict
            }
            rule_actions.append(action_config)
        elif action.actionType == 4:
            publish_dict = PublishActionSchema().dump(action.config).data
            publish_dict['taskID'] = generate_uuid()
            publish_json_func = PROTOCOL_PUBLISH_JSON_FUNC.get(publish_dict['protocol'])
            if not publish_json_func:
                raise FormInvalid(field='cloudProtocol')
            publish_json = publish_json_func(publish_dict)
            action_config = {
                'publish': {
                    'json': json.dumps(publish_json)
                }
            }
            rule_actions.append(action_config)
        elif action.actionType == 5:
            mqtt_dict = MqttActionSchema().dump(action.config).data
            action_config = {
                'mqtt': mqtt_dict
            }
            rule_actions.append(action_config)
    rule_json = {
        'id': rule.id,
        'sql': rule.sql,
        'enabled': rule.enable == 1,
        'actions': rule_actions
    }
    return rule_json


def stream_rule_http(method: AnyStr, **kwargs):
    with SyncHttp() as sync_http:
        response = getattr(sync_http, method)(**kwargs)

    if response.responseCode not in [200, 201]:
        db.session.rollback()
        raise InternalError(field='stream')
    return response
