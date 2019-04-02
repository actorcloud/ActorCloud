from flask import jsonify, g
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import Tag, User, ClientTag, Client
from . import bp
from ..schemas import TagSchema


@bp.route('/tags')
@auth.login_required
def list_tags():
    query = Tag.query \
        .join(User, User.id == Tag.userIntID) \
        .with_entities(Tag, User.username.label('createUser'))
    records = query.pagination()

    tags_uid = [tag['tagID'] for tag in records.get('items')]
    base_query = db.session \
        .query(ClientTag.c.tagID, func.count(ClientTag.c.deviceIntID)) \
        .join(Client, Client.id == ClientTag.c.deviceIntID) \
        .filter(ClientTag.c.tagID.in_(tags_uid)) \
        .group_by(ClientTag.c.tagID)

    device_count = base_query.filter(Client.type == 1).all()
    device_count_dict = dict(device_count)

    gateway_count = base_query.filter(Client.type == 2).all()
    gateway_count_dict = dict(gateway_count)

    for tag in records.get('items'):
        tag_uid = tag.get('tagID')
        tag['deviceCount'] = device_count_dict.get(tag_uid, 0)
        tag['gatewayCount'] = gateway_count_dict.get(tag_uid, 0)

    return jsonify(records)


@bp.route('/tags/<int:tag_id>')
@auth.login_required
def get_tag(tag_id):
    record = Tag.query \
        .filter(Tag.id == tag_id) \
        .to_dict()
    return jsonify(record)


@bp.route('/tags', methods=['POST'])
@auth.login_required
def create_tag():
    request_dict = TagSchema.validate_request()
    request_dict['userIntID'] = g.user_id
    tag = Tag()
    created_tag = tag.create(request_dict)
    record = created_tag.to_dict()
    return jsonify(record), 201


@bp.route('/tags/<int:tag_id>', methods=['PUT'])
@auth.login_required
def update_tag(tag_id):
    query_tag = Tag.query.filter(Tag.id == tag_id).first_or_404()
    request_dict = TagSchema.validate_request(obj=query_tag)
    updated_tag = query_tag.update(request_dict)
    record = updated_tag.to_dict()
    return jsonify(record)


@bp.route('/tags', methods=['DELETE'])
@auth.login_required
def delete_tag():
    delete_ids = get_delete_ids()
    query_results = Tag.query.filter(Tag.id.in_(delete_ids)).many()
    try:
        for query_result in query_results:
            db.session.delete(query_result)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
