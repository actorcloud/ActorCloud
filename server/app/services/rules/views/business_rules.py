from typing import AnyStr

from flask import jsonify, request, current_app
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ReferencedError, FormInvalid, InternalError
)
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    User, BusinessRule, Action, BusinessRuleAction
)
from . import bp
from ..schemas import BusinessRuleSchema, AlertActionSchema, UpdateBusinessRuleSchema


@bp.route('/business_rules')
@auth.login_required
def list_business_rules():
    query = BusinessRule.query \
        .with_entities(BusinessRule.id, BusinessRule.ruleName, BusinessRule.sql,
                       BusinessRule.enable, BusinessRule.remark)

    records = query.pagination()
    return jsonify(records)


@bp.route('/business_rules', methods=['POST'])
@auth.login_required
def create_business_rule():
    request_dict = BusinessRuleSchema.validate_request()
    business_rule = BusinessRule()
    new_rule = business_rule.create(request_dict, commit=False)

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


@bp.route('/business_rules/<int:rule_id>')
@auth.login_required
def view_business_rule(rule_id):
    record = BusinessRule.query \
        .join(User, User.id == BusinessRule.userIntID) \
        .with_entities(BusinessRule, User.username.label('createUser')) \
        .filter(BusinessRule.id == rule_id) \
        .to_dict()

    actions = db.session.query(Action.actionName) \
        .join(BusinessRuleAction) \
        .filter(BusinessRuleAction.c.businessRuleIntID == rule_id) \
        .all()
    action_names = [action.actionName for action in actions]
    record['actionNames'] = action_names
    return jsonify(record)


@bp.route('/business_rules/<int:rule_id>', methods=['PUT'])
@auth.login_required
def update_business_rule(rule_id):
    business_rule = BusinessRule.query \
        .filter(BusinessRule.id == rule_id) \
        .first_or_404()
    old_enable = business_rule.enable
    request_dict = UpdateBusinessRuleSchema.validate_request(obj=business_rule)
    updated_business_rule = business_rule.update(request_dict, commit=False)

    action_ids = request.get_json().get('actions')
    if action_ids:
        update_actions = Action.query \
            .filter(Action.id.in_(action_ids)) \
            .many()
        updated_business_rule.actions = update_actions
    rule_json = get_rule_json(updated_business_rule)
    url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule_id}"
    stream_rule_http('put', url=url, json=rule_json)
    changed = old_enable != updated_business_rule.enable
    if changed:
        switch = 'start' if updated_business_rule.enable else 'stop'
        switch_url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule_id}/{switch}"
        stream_rule_http('put', url=switch_url)
    db.session.commit()
    record = updated_business_rule.to_dict()
    return jsonify(record)


@bp.route('/business_rules', methods=['DELETE'])
@auth.login_required
def delete_business_rule():
    try:
        ids = get_delete_ids()
        rules = BusinessRule.query \
            .filter(BusinessRule.id.in_(ids)) \
            .many()
        for rule in rules:
            db.session.delete(rule)
            url = f"{current_app.config.get('STREAM_RULE_URL')}/{rule.id}"
            stream_rule_http('delete', url=url)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def get_rule_json(business_rule):
    rule_actions = []
    for action in business_rule.actions:
        if action.actionType == 1:
            alert_dict = AlertActionSchema().dump(action.config).data
            action_config = {
                'webhook': {
                    **alert_dict,
                    'url': current_app.config.get('CURRENT_ALERT_URL'),
                    'ruleIntID': business_rule.id

                }
            }
            rule_actions.append(action_config)
    rule_json = {
        'id': business_rule.id,
        'sql': business_rule.sql,
        'enabled': True if business_rule.enable == 1 else False,
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
