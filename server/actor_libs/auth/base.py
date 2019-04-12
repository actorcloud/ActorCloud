# coding: utf-8

import arrow
from flask import current_app, request, g
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

from actor_libs.errors import AuthFailed
from app.models import Application, User


__all__ = ['basic_auth', 'token_auth']


def basic_auth(username, password) -> bool:
    """ HTTP basic authorization """

    query_result = Application.query \
        .join(User, User.id == Application.userIntID) \
        .with_entities(Application, User) \
        .filter(Application.appStatus == 1, User.enable == 1,
                Application.appID == username).first()
    if not query_result:
        raise AuthFailed(field='appID')
    application, user = query_result
    # Verify that app is available
    date_now = arrow.now().naive
    if application.expiredAt and date_now > application.expiredAt:
        raise AuthFailed(field='expiredAt')
    if application.appToken != password:
        raise AuthFailed(field='appToken')
    g.user_id: int = user.id
    g.tenant_uid: str = user.tenantID
    g.role_id: int = application.roleIntID
    g.app_uid: str = application.appID
    user.lastRequestTime = date_now  # Update user active time
    user.update()
    return True


def token_auth(token) -> bool:
    """ HTTP bearer token authorization """

    jwt = JWT(current_app.config['SECRET_KEY'])
    try:
        data = jwt.loads(token)
    except Exception:
        raise AuthFailed(field='token')

    if data.get('consumer_id'):
        # todo consumer user auth ?
        ...
    else:
        # Normal user
        if ('user_id' or 'role_id') not in data:
            raise AuthFailed(field='token')
        if data['role_id'] != 1 and not data.get('tenant_uid'):
            raise AuthFailed(field='token')
        user = User.query \
            .filter(User.roleIntID == data['role_id'], User.id == data['user_id'],
                    User.tenantID == data['tenant_uid']).first()
        if not user:
            raise AuthFailed(field='token')
        g.user_id: int = user.id
        g.tenant_uid: str = user.tenantID
        g.role_id: int = user.roleIntID
        g.app_uid: str = None
        g.user_auth_type: int = user.userAuthType
        user.lastRequestTime = arrow.now().naive
        user.update()
    return True
