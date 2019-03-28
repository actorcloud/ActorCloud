from collections import defaultdict

from app import auth
from flask import jsonify, g, request
from sqlalchemy import or_, func

from actor_libs.database.orm import db
from app.models import DictCode, Role, Tag
from . import bp


@bp.route('/emq_select/dict_code')
@auth.login_required(permission_required=False)
def list_dict_code():
    record = defaultdict(list)
    dict_code_values = db.session \
        .query(DictCode.code, DictCode.codeLabel,
               func.coalesce(DictCode.codeStringValue, DictCode.codeValue).label('value')) \
        .all()
    for dict_code in dict_code_values:
        code, label, value = dict_code
        option = {
            'value': value,
            'label': label
        }
        record[code].append(option)
    return jsonify(record)


@bp.route('/emq_select/app_roles')
@bp.route('/emq_select/roles')
@auth.login_required(permission_required=False)
def list_emq_select_roles():
    role_type = 2 if request.path.endswith('/app_roles') else 1
    query = Role.query \
        .filter(~Role.id.in_([1, 2, 3])) \
        .filter(Role.roleType == role_type)

    if g.role_id != 1 and g.tenant_uid:
        query = query \
            .filter(or_(Role.tenantID == g.tenant_uid, Role.isShare == 1))
    roles = [
        {
            'value': role.id,
            'label': role.roleName
        }
        for role in query.all()
    ]
    return jsonify(roles)


@bp.route('/emq_select/tags')
@auth.login_required(permission_required=False)
def emq_select_tags():
    records = Tag.query \
        .with_entities(Tag.tagID.label('value'),
                       Tag.tagName.label('label')) \
        .select_options()
    return jsonify(records)
