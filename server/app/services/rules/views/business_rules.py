from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ReferencedError, FormInvalid
)
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    User, BusinessRule, Action, BusinessRuleAction
)
from . import bp
from ..schemas import BusinessRuleSchema


@bp.route('/business_rules')
@auth.login_required
def list_business_rules():
    query = BusinessRule.query \
        .with_entities(BusinessRule.id, BusinessRule.ruleName, BusinessRule.sql,
                       BusinessRule.enable)

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
    request_dict = BusinessRuleSchema.validate_request(obj=business_rule)
    updated_business_rule = business_rule.update(request_dict, commit=False)

    action_ids = request.get_json().get('actions')
    update_actions = Action.query \
        .filter(Action.id.in_(action_ids)) \
        .many()
    updated_business_rule.actions = update_actions

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
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
