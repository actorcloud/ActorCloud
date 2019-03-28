from flask import g, jsonify, request

from app import auth

from app.models import User, LoginLog

from . import bp


@bp.route('/login_logs')
@auth.login_required
def list_login_logs():
    query = LoginLog.query \
        .join(User, LoginLog.userIntID == User.id) \
        .with_entities(LoginLog, User.username)

    username = request.args.get('username_like')
    if username:
        query = query.filter(User.username.like(u'%{0}%'.format(username)))

    if g.role_id not in [1, 2, 3]:
        query = query.filter(User.id == g.user_id)
    records = query.pagination(code_list=['isLogged'])
    return jsonify(records)
