from datetime import datetime

from flask import jsonify, g, request, current_app
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError, ParameterInvalid, AuthFailed
from actor_libs.send_mails import send_html
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import User, Role, Invitation, UserGroup, Group
from . import bp
from ..schemas import UserSchema, UpdateUserSchema, ResetPasswordSchema, InvitationSchema


@bp.route('/users')
@auth.login_required
def list_users():
    query = User.query \
        .join(Role, Role.id == User.roleIntID) \
        .with_entities(User, Role.roleName)
    if g.role_id != 1:
        query = query.filter(~Role.id.in_([2, 3]))
    records = query.pagination()
    return jsonify(records)


@bp.route('/users/<int:user_id>')
@auth.login_required
def get_user(user_id):
    record = User.query \
        .join(Role, Role.id == User.roleIntID) \
        .filter(User.id == user_id) \
        .with_entities(User, Role.roleName.label('roleName')).to_dict()
    user_type = record['userAuthType']
    if user_type == 2:
        # list user management groups
        user_groups = Group.query.join(UserGroup, UserGroup.c.groupID == Group.groupID) \
            .filter(UserGroup.c.userIntID == user_id) \
            .with_entities(Group.id, Group.groupID, Group.groupName).all()
        groups_uid = []
        groups_index = []
        for group in user_groups:
            groups_uid.append(group.groupID)
            groups_index.append({'value': group.id, 'label': group.groupName})
        record['groups'] = groups_uid
        record['groupsIndex'] = groups_index
    return jsonify(record)


@bp.route('/users', methods=['POST'])
@auth.login_required
def new_user():
    request_dict = UserSchema.validate_request()
    request_dict['lastRequestTime'] = datetime.now()
    user = User()
    user_dict = user.create(request_dict).to_dict()
    user_dict['token'] = user.generate_auth_token()
    return jsonify(user_dict), 201


@bp.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    query = User.query.filter(User.id == user_id)
    if g.role_id != 1:
        query = query.filter(~User.roleIntID.in_([1, 2, 3]))
    user = query.first_or_404()
    request_dict = UpdateUserSchema.validate_request(obj=user)
    updated_user = user.update(request_dict)
    record = updated_user.to_dict()
    return jsonify(record)


@bp.route('/users', methods=['DELETE'])
@auth.login_required
def delete_user():
    user_ids = get_delete_ids()
    try:
        if g.role_id == 1:
            User.query \
                .filter(User.id.in_(user_ids)) \
                .filter(User.roleIntID != 1) \
                .delete(synchronize_session='fetch')
        else:
            User.query \
                .filter(User.id.in_(user_ids)) \
                .filter(~User.roleIntID.in_([1, 2, 3])) \
                .filter(User.id != g.user_id) \
                .filter(User.tenantID == g.tenant_uid) \
                .delete(synchronize_session='fetch')
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/reset_password', methods=['PUT'])
@auth.login_required(permission_required=False)
def reset_password():
    user = User.query.filter(User.id == g.user_id).first_or_404()

    request_dict = ResetPasswordSchema.validate_request(obj=user)
    _password = request_dict.get('oldPassword')
    if user.check_password(_password):
        user.lastRequestTime = datetime.now()
    else:
        raise AuthFailed(field='oldPassword')
    updated_user = user.update(request_dict)
    record = updated_user.to_dict()
    return jsonify(record)


@bp.route('/invitations')
@auth.login_required
def list_invitations():
    query = Invitation.query \
        .join(Role, Role.id == Invitation.roleIntID) \
        .join(User, User.id == Invitation.userIntID) \
        .with_entities(Invitation, Role.roleName, User.username)

    records = query.pagination(code_list=['inviteStatus'])
    return jsonify(records)


@bp.route('/invitations/<int:invite_id>')
@auth.login_required
def get_invitation(invite_id):
    record = Invitation.query \
        .filter(Invitation.id == invite_id) \
        .to_dict()
    return jsonify(record)


@bp.route('/invitations', methods=['POST'])
@auth.login_required
def new_invitation():
    request_dict = InvitationSchema.validate_request()
    request_dict['userIntID'] = g.user_id
    request_dict['tenantID'] = g.tenant_uid
    invitation = Invitation()
    invitation_dict = invitation.create(request_dict).to_dict()
    user = User.query.filter(User.id == g.user_id).first_or_404()
    username = user.email
    email_title = current_app.config.get('EMAIL_TITLE')
    site_domain = current_app.config.get('SITE_DOMAIN')
    site_name = current_app.config.get('SITE_NAME')
    send_invite_mail(invitation, username, email_title, site_domain, site_name)
    return jsonify(invitation_dict), 201


@bp.route('/invitations', methods=['DELETE'])
@auth.login_required
def delete_invitations():
    try:
        ids = [int(i) for i in request.args.get('ids').split(',')]
    except ValueError:
        raise ParameterInvalid(field='ids')
    try:
        Invitation.query \
            .filter(Invitation.id.in_(ids)) \
            .filter(Invitation.tenantID == g.tenant_uid) \
            .delete(synchronize_session='fetch')
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def send_invite_mail(invitation, username, email_title, site_domain, site_name):
    token = invitation.generate_auth_token()
    email = invitation.inviteEmail
    link = f'{site_domain}/signup?i={token}'

    if g.language == 'zh':
        content = f"{username} 用户邀请您加入 {site_name}"
        click_tips = f"请点击此链接加入 {site_name}"
    else:
        content = f"{username} invites you to join {site_name}"
        click_tips = f"Please click this link to join {site_name}"
    email_html = _EMAIL_HTML.format(content=content, link=link, click_tips=click_tips)
    send_html(email, email_title, email_html)


_EMAIL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
  <p>{content}, <a href="{link}">{click_tips}</a></p>
</body>
</html>
"""
