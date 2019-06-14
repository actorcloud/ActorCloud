import shutil

from flask import (
    jsonify, request, current_app, send_from_directory, g
)

from actor_libs.database.orm import db
from actor_libs.errors import APIException, DataNotFound
from app import auth
from app.models import SystemInfo, UploadInfo
from app.schemas import LogoInfoSchema
from . import bp


@bp.route('/system_info')
@auth.login_required
def get_system_info():
    system_info_list = SystemInfo.query.all()
    records = {}
    for system_info in system_info_list:
        records[system_info.key] = system_info.value
    return jsonify(records)


@bp.route('/system_info', methods=['PUT'])
@auth.login_required
def update_system_info():
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    if g.tenant_uid:
        raise DataNotFound(field='url')
    system_info_list = SystemInfo.query.all()
    for system_info in system_info_list:
        new_value = request_dict.get(system_info.key)
        if not new_value:
            continue
        if isinstance(new_value, bytes):
            new_value = new_value.decode('utf-8')
        system_info.value = new_value
    db.session.commit()
    return ''


@bp.route('/broker_info')
@auth.login_required(permission_required=False)
def get_broker_info():
    broker = SystemInfo.query.filter(SystemInfo.key.ilike('%Broker')).all()
    broker_info = {row.key: row.value for row in broker}
    return jsonify(broker_info)


@bp.route('/logo_info')
@auth.login_required
def get_logo_info():
    default_logo = dict(
        icon='favicon.ico', sign='sign.png', logo='logo.png', logoDark='logo-dark.png'
    )
    records = {}
    api_version = current_app.config['ACTORCLOUD_API']
    for key, value in default_logo.items():
        result = {
            'name': value,
            'uploadID': 0,
            'url': f'{api_version}/backend_static?fileType=image&filename={value}'
        }
        records[key] = [result]
    return jsonify(records)


@bp.route('/logo_info', methods=['PUT'])
@auth.login_required
def update_logo_info():
    request_dict = LogoInfoSchema.validate_request()
    default_logo = dict(
        icon='favicon.ico', sign='sign.png', logo='logo.png', logoDark='logo-dark.png'
    )
    for key, value in default_logo.items():
        new_value = request_dict.get(key)
        if new_value:
            upload_info = UploadInfo.query \
                                    .filter(UploadInfo.id == new_value) \
                                    .first()
            if upload_info:
                copy_image(upload_info.fileName, value)
    db.session.commit()
    return ''


@bp.route('/backend_static')
def backend():
    file_type = request.args.get('fileType', None, type=str)
    filename = request.args.get('filename', None, type=str)
    if file_type != 'image':
        raise DataNotFound(field='url')
    dst_path = current_app.config.get('LOGOS_PATH')
    return send_from_directory(dst_path, filename)


def copy_image(src_name, dst_name):
    src_path = current_app.config.get('UPLOADED_IMAGES_DEST')
    dst_path = current_app.config.get('LOGOS_PATH')
    shutil.copyfile(src_path + src_name, dst_path + dst_name)
