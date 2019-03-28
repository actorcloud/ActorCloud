from datetime import datetime

from flask import jsonify, g, request, current_app
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError, ParameterInvalid, AuthFailed
from actor_libs.send_mails import send_html
from app import auth
from app.models import User, Role, DictCode, Invitation, Tag
from . import bp
from ..schemas import UserSchema, UpdateUserSchema, ResetPasswordSchema, InvitationSchema


@bp.route('/users')
@auth.login_required
def list_users():
    query = User.query \
        .join(Role, Role.id == User.roleIntID) \
        .with_entities(User, Role.roleName)

    if g.role_id != 1:
        query = query \
            .filter(User.tenantID == g.tenant_uid) \
            .filter(~Role.id.in_([2, 3]))
    records = query.pagination()
    return jsonify(records)


@bp.route('/users/<int:user_id>')
@auth.login_required
def get_user(user_id):
    query = User.query.join(Role, Role.id == User.roleIntID).filter(User.id == user_id)
    if g.role_id != 1 and g.tenant_uid:
        query = query.filter(User.tenantID == g.tenant_uid)
    user, role_name = query.with_entities(User, Role.roleName).first_or_404()
    record = user.to_dict()
    record['roleName'] = role_name

    if user.userAuthType == 2:
        user_tags = user.tags.with_entities(Tag.id, Tag.tagID, Tag.tagName).all()
        tags_uid = []
        tags_index = []
        tags_uid_append = tags_uid.append
        tags_index_append = tags_index.append
        for tag in user_tags:
            tags_uid_append(tag.tagID)
            tags_index_append({'value': tag.id, 'label': tag.tagName})
        record['tags'] = tags_uid
        record['tagIndex'] = tags_index
    return jsonify(record)


@bp.route('/users', methods=['POST'])
@auth.login_required
def new_user():
    request_dict = UserSchema.validate_request()
    request_dict['lastRequestTime'] = datetime.now()
    request_dict['tenantID'] = g.tenant_uid
    user_auth_type = request_dict.get('userAuthType')

    tags_uid = []
    if user_auth_type == 2:
        tags_uid = request_dict.get('tags')
        tags = db.session.query(Tag) \
            .filter(Tag.tagID.in_(tags_uid)) \
            .all()
        request_dict['tags'] = tags
    else:
        request_dict.pop('tags', None)

    user = User()
    user_dict = user.create(request_dict).to_dict()
    user_dict['token'] = user.generate_auth_token()
    user_dict['tags'] = tags_uid
    return jsonify(user_dict), 201


@bp.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    query = User.query.filter(User.id == user_id, User.roleIntID != 1)
    if g.role_id != 1 and g.tenant_uid:
        query = query.filter(~User.roleIntID.in_([2, 3]),
                             User.tenantID == g.tenant_uid)
    user = query.first_or_404()

    request_dict = UpdateUserSchema.validate_request(obj=user)
    user_auth_type = request_dict.get('userAuthType')
    tags_uid = []

    if user_auth_type == 2:
        tags_uid = request_dict.get('tags')
        tags = Tag.query \
            .filter(Tag.tagID.in_(tags_uid)) \
            .all()
        request_dict['tags'] = tags
    else:
        request_dict.pop('tags', None)
    if user.userAuthType != user_auth_type and user_auth_type == 1:
        request_dict['tags'] = []

    updated_user = user.update(request_dict)
    record = updated_user.to_dict()
    record['tags'] = tags_uid
    return jsonify(record)


@bp.route('/users', methods=['DELETE'])
@auth.login_required
def delete_user():
    try:
        ids = [int(i) for i in request.args.get('ids').split(',')]
    except ValueError:
        raise ParameterInvalid(field='ids')
    try:
        if g.role_id == 1:
            User.query \
                .filter(User.id.in_(ids)) \
                .filter(User.roleIntID != 1) \
                .delete(synchronize_session='fetch')
        else:
            User.query \
                .filter(User.id.in_(ids)) \
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
        .join(DictCode, DictCode.codeValue == Invitation.inviteStatus) \
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
    link = 'https://%s/signup?i=%s' % (site_domain, token)

    content = u" 用户 %s 邀请您加入 %s" % (username, site_name)
    link = (u'''<a href=%s>''' % link) + link + u'''</a>'''
    content = u'''
            <html>
              <head>
                <meta charset="utf-8">
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
              </head>
              <div style="background-color:#F2F2F2; padding:30px 0; color:#2D3238;">
                <div style="display:block; background-color:#fff; border-radius:6px;
                            margin:0 auto 10px; width:80%; padding:60px 20px;">
                  <div style="margin-bottom: 50px; text-align: center;">
                    <img src="http://emqtt.com/static/img/emqlogo.jpg"
                         style="width: 100px;">
                    <h4 style="font-weight: 600; font-size: 18px;">
                    ''' + content + u'，请点击该链接完成注册：' + link + u'''</a></h4>
                  </div>
                </div>
            </html>
            '''
    send_html(email, email_title, content)
