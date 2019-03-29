import random
import string
from collections import defaultdict
from datetime import datetime

from flask import current_app, jsonify, request
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

from actor_libs.database.orm import db
from actor_libs.errors import (
    AuthFailed, DataNotFound, FormInvalid
)
from app import auth
from app.models import (
    Invitation, LoginLog, Resource, Tenant, UploadInfo, User
)
from . import bp
from ..schemas import LoginSchema, TenantSchema, UserSchema


@bp.route('/login', methods=['POST'])
def login():
    request_dict = LoginSchema.validate_request()
    remember = request_dict.get('remember', False)

    query_login = db.session.query(User, Tenant) \
        .outerjoin(Tenant, Tenant.tenantID == User.tenantID) \
        .filter(User.email == request_dict.get('email'),
                User.enable == 1) \
        .first()
    if not query_login:
        raise AuthFailed(field='email')

    user, tenant = query_login
    if not user or (tenant and tenant.enable != 1):
        raise AuthFailed(field='email')

    user.loginTime = datetime.now()
    is_logged = 1 if user.check_password(request_dict.get('password')) else 0
    login_log = LoginLog(
        userIntID=user.id,
        IP=request.headers.get('X-Real-Ip') or request.remote_addr,
        loginTime=datetime.now(),
        isLogged=is_logged
    )
    db.session.add(login_log)
    db.session.commit()
    if not is_logged:
        raise AuthFailed(field='password')

    # logo path
    logo = '/backend_static/images/logo.png'
    logo_dark = '/backend_static/images/logo-dark.png'
    if tenant:
        logo_info = db.session.query(UploadInfo.fileName) \
            .filter(UploadInfo.id == tenant.logo) \
            .first()
        logo_dark_info = db.session.query(UploadInfo.fileName) \
            .filter(UploadInfo.id == tenant.logoDark) \
            .first()
        if logo_info:
            logo = f'/api/v1/download?fileType=image&filename={logo_info.fileName}'
        if logo_dark_info:
            logo_dark = f'/api/v1/download?fileType=image&filename={logo_dark_info.fileName}'

    if isinstance(user.tenantID, str):
        tenant_type_dict = {'P': 1, 'C': 2}
        tenant_type = tenant_type_dict.get(user.tenantID[0])
    else:
        tenant_type = 0

    # Get user menu tree,tabs and permissions
    menus_tree, tabs, permissions = generate_tabs_and_tree(
        role_id=user.roleIntID, tenant_uid=user.tenantID
    )

    if current_app.config.get('showProductsMall') != 1:
        show_products_mall = 0
    else:
        show_products_mall = 1

    return jsonify({
        'userIntID': user.id,
        'username': user.username,
        'tenantType': tenant_type,
        'token': user.generate_auth_token(remember=remember),
        'menus': menus_tree,
        'tabs': tabs,
        'permissions': permissions,
        'show_products_mall': show_products_mall,
        'logo': logo,
        'logoDark': logo_dark
    }), 201


@bp.route('/signup', methods=['POST'])
def signup():
    user_dict = UserSchema.validate_request()
    token = request.get_json().get('token')

    if not token:
        normal_user = signup_normal_user(normal_user=user_dict)
        user_dict.update(normal_user)
    else:
        invite_user = signup_invite_user(token)
        user_dict.update(invite_user)
    new_user = User(enable=1)
    for key, value in user_dict.items():
        if hasattr(new_user, key):
            setattr(new_user, key, value)
    db.session.add(new_user)
    db.session.commit()
    created_user = new_user.to_dict()
    created_user['token'] = new_user.generate_auth_token()
    created_user['userIntID'] = created_user.get('id')
    return jsonify(created_user), 201


def signup_normal_user(normal_user=None):
    tenant_dict = TenantSchema.validate_request()
    tenant_type = tenant_dict.get('tenantType')
    tenant_uid = random_tenant_uid(tenant_type)
    tenant_dict['contactEmail'] = normal_user['email']
    tenant_dict['tenantID'] = tenant_uid

    phone = normal_user.get('phone') or tenant_dict.get('contactPhone')
    tenant_dict['contactPhone'] = phone
    normal_user['phone'] = phone

    new_tenant = Tenant()
    for key, value in tenant_dict.items():
        if hasattr(new_tenant, key):
            setattr(new_tenant, key, value)
    db.session.add(new_tenant)
    db.session.flush()

    # Role
    if tenant_type == 1:
        normal_user['roleIntID'] = 3
    elif tenant_type == 2:
        normal_user['roleIntID'] = 2
    else:
        raise FormInvalid(field='tenantType')
    normal_user['tenantID'] = tenant_uid
    return normal_user


def signup_invite_user(token):
    jwt = JWT(current_app.config['SECRET_KEY'])
    try:
        data = jwt.loads(token)
    except Exception:
        raise FormInvalid(field='token')

    if not data.get('invitation_id'):
        raise FormInvalid(field='invitation')
    invitation = Invitation.query \
        .join(Tenant, Tenant.tenantID == Invitation.tenantID) \
        .filter(Invitation.id == data.get('invitation_id'),
                Invitation.inviteStatus == 0, Tenant.enable == 1) \
        .first()
    if not invitation:
        raise DataNotFound(field='invitation')
    invitation.inviteStatus = 1
    invite_user = {
        'roleIntID': invitation.roleIntID,
        'tenantID': invitation.tenantID
    }
    return invite_user


def random_tenant_uid(tenant_type):
    tenant_uid = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    if tenant_type == 1:
        tenant_uid = 'P' + tenant_uid
    else:
        tenant_uid = 'C' + tenant_uid
    if Tenant.query.filter_by(tenantID=tenant_uid).count() > 0:
        tenant_uid = random_tenant_uid(tenant_type)
    return tenant_uid


def generate_tabs_and_tree(role_id=None, tenant_uid=None):
    permission_resources = auth.permission_resources(role_id, tenant_uid)
    root_resources = Resource.query \
        .filter(Resource.level == 1, Resource.enable == 1)\
        .order_by(Resource.order).all()

    permission_codes = get_permission_codes(permission_resources=permission_resources)
    menus_tree = get_menus_tree(
        root_resources=root_resources,
        permission_codes=permission_codes
    )
    menus_tree = [menus for menus in menus_tree if menus.get('children')]
    permissions = get_permissions(permission_resources=permission_resources)
    tabs = get_tabs(permission_codes)
    return menus_tree, tabs, permissions


def get_permissions(permission_resources=None):
    """
    {'/users': ['GET', 'POST']}
    """
    permission_dict = defaultdict(list)
    for resource in permission_resources:
        if resource.method is not None:
            permission_dict[resource.url].append(resource.method)
    return permission_dict


def get_permission_codes(permission_resources):
    """
    Generate a list of resource code that the user can access to
    :param permission_resources: Resources that user can access to
    :return: a list of resource code that the user can access to
    """
    permission_codes = []

    for resource in permission_resources:
        permission_codes.append(resource.code)
        parent = resource.parent
        while parent:
            permission_codes.append(parent.code)
            parent = parent.parent
    return set(permission_codes)


def get_tabs(permission_codes):
    """
    Format:
        "tabs": {"users": [{"code": "users-invitations",
                 "url": "/users/invitations"}]}
    :param permission_codes: permission codes
    :return: tabs
    """
    if not isinstance(permission_codes, set):
        raise Exception("permission_codes must be a set!")
    tabs_dict = defaultdict(list)
    tab_resources = Resource.query \
        .filter(tabs=1, enable=1) \
        .order_by(Resource.order).all()
    tab_resources = [
        resource for resource in tab_resources
        if resource.code in permission_codes
    ]
    for resource in tab_resources:
        child_resources = sorted(
            resource.children, key=lambda child_resource: child_resource.order)
        for child in child_resources:
            if child.code not in permission_codes or child.enable == 0:
                continue
            child_dict = {
                'code': child.code,
                'url': child.url,
                'order': child.order
            }
            tabs_dict[resource.code].append(child_dict)
    return tabs_dict


def get_menus_tree(root_resources=None, permission_codes=None):
    root_resources = [
        resource for resource in root_resources
        if resource.code in permission_codes
    ]
    sorted_root_resources = sorted(root_resources, key=lambda root_resource: root_resource.order)
    menus_tree = []
    for resource in sorted_root_resources:
        menu_dict = {
            'id': resource.id,
            'code': resource.code,
            'url': resource.url,
            'order': resource.order,
            'icon': resource.icon,
            'tabs': resource.tabs
        }
        children = resource.children
        if children:
            children_children = get_menus_tree(children, permission_codes)
            if children_children:
                menu_dict['children'] = children_children
        menus_tree.append(menu_dict)
    return menus_tree
