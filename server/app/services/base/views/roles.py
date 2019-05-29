from flask import jsonify, g, request
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    ReferencedError, PermissionDenied, ParameterInvalid
)
from app import auth
from app.models import Role, Resource, Permission
from . import bp
from ..schemas import RoleSchema


@bp.route('/roles')
@bp.route('/app_roles')
@auth.login_required
def list_roles():
    query = Role.query.filter(Role.id != 1, Role.id != g.role_id)
    if request.path.find('app') >= 0:
        query = query.filter(Role.roleType == 2)
    else:
        query = query.filter(Role.roleType == 1)
    records = query.pagination()
    return jsonify(records)


@bp.route('/roles/<int:role_id>')
@bp.route('/app_roles/<int:role_id>')
@auth.login_required
def get_role(role_id):
    query = Role.query.filter(Role.id == role_id, Role.id != g.role_id)
    query_role = check_request(query).first_or_404()
    role = query_role.to_dict()
    if g.role_id != 1 and g.tenant_uid:
        permission_resources = auth.permission_resources(role_id, g.tenant_uid)
        ids = [resource.id for resource in permission_resources]
    else:
        permission_resources = db.session.query(Permission.resourceIntID) \
            .filter(Permission.roleIntID == role_id) \
            .all()
        ids = [resource[0] for resource in permission_resources]
    role['permissions'] = ids
    return jsonify(role)


@bp.route('/roles', methods=['POST'])
@bp.route('/app_roles', methods=['POST'])
@auth.login_required
def create_role():
    request_dict = RoleSchema.validate_request()
    request_permissions = request_dict.get('permissions')
    validate_permissions(request_permissions)
    request_dict['tenantID'] = g.tenant_uid
    if request.path.find('app') >= 0:
        request_dict['roleType'] = 2
    else:
        request_dict['roleType'] = 1
    role = Role()
    new_role = role.create(request_dict)
    record = new_role.to_dict()
    insert_permissions(record.get('id'), request_permissions)
    return jsonify(record), 201


@bp.route('/roles/<int:role_id>', methods=['PUT'])
@bp.route('/app_roles/<int:role_id>', methods=['PUT'])
@auth.login_required
def update_role(role_id):
    # Filter admin role and user's role
    query = Role.query \
        .filter(and_(Role.id == role_id, Role.id != g.role_id)) \
        .filter(~Role.id.in_([1, 2, 3]))

    role = check_request(query).first_or_404()
    request_dict = RoleSchema.validate_request(obj=role)
    request_permissions = request_dict.get('permissions')
    validate_permissions(request_permissions)

    request_dict['tenantID'] = g.tenant_uid
    updated_role = role.update(request_dict)
    record = updated_role.to_dict()
    old_permissions = Permission.query \
        .filter(Permission.roleIntID == role_id) \
        .all()
    for old_permission in old_permissions:
        db.session.delete(old_permission)
    insert_permissions(role_id, request_permissions)
    return jsonify(record)


@bp.route('/roles', methods=['DELETE'])
@bp.route('/app_roles', methods=['DELETE'])
@auth.login_required
def delete_role():
    try:
        ids = [int(i) for i in request.args.get('ids').split(',')]
    except ValueError:
        raise ParameterInvalid(field='ids')
    try:
        query = Role.query \
            .filter(Role.id.in_(ids)) \
            .filter(~Role.id.in_([1, 2, 3])) \
            .filter(Role.id != g.role_id) \
            .filter(Role.tenantID == g.tenant_uid)
        check_request(query).delete(synchronize_session='fetch')
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/all_app_permissions')
@bp.route('/all_permissions')
@auth.login_required(permission_required=False)
def list_all_permissions():
    query = Resource.query
    if request.path.find('app') >= 0:
        # App permission
        query = query.filter(Resource.code.in_(['device_manage', 'alert_manage', 'business_rules']))
        role_id = db.session.query(Role.id) \
            .filter(Role.roleName == u'超级应用', Role.roleType == 2,
                    Role.isShare == 1, Role.tenantID.is_(None)) \
            .first()
        role_id = role_id
    else:
        role_id = g.role_id
        query = query.filter_by(level=1)
    root_resources = query.order_by(Resource.order).all()

    permission_resources = auth.permission_resources(role_id, g.tenant_uid)
    permission_codes = get_permission_code_or_id(permission_resources, return_type='code')
    permission_tree = get_permission_tree(root_resources=root_resources,
                                          permission_codes=permission_codes)
    return jsonify(permission_tree)


def insert_permissions(role_id, request_permissions):
    permissions = []
    for resource_id in request_permissions:
        permission = Permission()
        permission.roleIntID = role_id
        permission.resourceIntID = resource_id
        permissions.append(permission)
    db.session.add_all(permissions)
    db.session.commit()


def check_request(query):
    if g.role_id != 1 and g.tenant_uid:
        if request.method == 'GET':
            query = query.filter(
                or_(Role.tenantID == g.tenant_uid, Role.isShare == 1))
        else:
            query = query.filter(Role.tenantID == g.tenant_uid)

    if request.path.find('app') >= 0:
        query = query.filter(Role.roleType == 2)
    else:
        query = query.filter(Role.roleType == 1)
    return query


def validate_permissions(request_permissions):
    """
    Compare request permissions and default permissions
    :raise PermissionDenied if request permission not in default permissions
    """

    permission_resources = auth.permission_resources(g.role_id, g.tenant_uid)
    permission_ids = get_permission_code_or_id(
        permission_resources, return_type='id')
    no_permissions = [
        per_id for per_id in request_permissions
        if per_id not in permission_ids
    ]
    if no_permissions:
        raise PermissionDenied()


def get_permission_code_or_id(permission_resources, return_type='code'):
    permission_codes = []

    for resource in permission_resources:
        parent = resource.parent
        while parent:
            if return_type == 'code':
                permission_codes.append(resource.code)
                permission_codes.append(parent.code)
            else:
                permission_codes.append(resource.id)
                permission_codes.append(parent.id)
            parent = parent.parent
    return set(permission_codes)


def get_permission_tree(root_resources=None, permission_codes=None):
    root_resources = [
        resource for resource in root_resources
        if resource.code in permission_codes
    ]
    sorted_root_resources = sorted(
        root_resources, key=lambda root_resource: root_resource.order)
    permission_tree = []
    for resource in sorted_root_resources:
        permission_dict = {
            'id': resource.id,
            'label': resource.code,
        }
        children = resource.children
        if children:
            children_children = get_permission_tree(children, permission_codes)
            if children_children:
                permission_dict['children'] = children_children
        permission_tree.append(permission_dict)
    return permission_tree
