from collections import defaultdict

from flask import jsonify, g, request
from sqlalchemy import or_

from app import auth
from app.models import DictCode, Role
from . import bp


@bp.route('/select_options/dict_code')
@auth.login_required(permission_required=False)
def list_dict_code():
    record = defaultdict(list)
    query_dict_code = DictCode.query.all()
    for dict_code in query_dict_code:
        if dict_code.codeValue is not None:
            code_value = dict_code.codeValue
        else:
            code_value = dict_code.codeStringValue
        option = {
            'value': code_value,
            'enLabel': dict_code.enLabel,
            'zhLabel': dict_code.zhLabel
        }
        record[dict_code.code].append(option)
    return jsonify(record)


@bp.route('/select_options/app_roles')
@bp.route('/select_options/roles')
@auth.login_required(permission_required=False)
def list_select_options_roles():
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

