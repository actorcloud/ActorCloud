from flask import request, jsonify, g
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid, ReferencedError, APIException
from app import auth
from app.models import DictCode, Message
from . import bp


@bp.route('/messages')
@auth.login_required
def list_messages():
    query = Message.query \
        .join(DictCode, DictCode.codeValue == Message.messageType) \
        .filter(DictCode.code == 'messageType') \
        .filter(or_(Message.tenantID == g.tenant_uid, Message.tenantID.is_(None)))

    msg_title = request.args.get('msgTitle_like')
    if msg_title:
        query = query \
            .filter(Message.msgTitle.ilike(u'%{0}%'.format(msg_title)))

    msg_type = request.args.get('messageType')
    if msg_type:
        query = query.filter(DictCode.codeValue == int(msg_type))

    records = query.pagination(code_list=['messageType'])
    return jsonify(records)


@bp.route('/messages/<int:msg_id>')
@auth.login_required
def get_message(msg_id):
    query = Message.query \
        .filter(Message.id == msg_id) \
        .filter(or_(Message.tenantID == g.tenant_uid,
                    Message.tenantID.is_(None))) \
        .first_or_404()
    record = query.to_dict(code_list=['messageType'])
    return jsonify(record)


@bp.route('/messages', methods=['DELETE'])
@auth.login_required
def delete_messages():
    try:
        ids = [int(i) for i in request.args.get('ids').split(',')]
    except ValueError:
        raise ParameterInvalid(field='ids')
    try:
        messages = Message.query \
            .filter(Message.id.in_(ids),
                    or_(Message.tenantID == g.tenant_uid,
                        Message.tenantID.is_(None))) \
            .all()
        for message in messages:
            if message.tenantID is None:
                raise APIException()
            db.session.delete(message)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
