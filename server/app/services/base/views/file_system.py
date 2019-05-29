import hashlib

import time
from flask import jsonify, g, request, send_from_directory, current_app
from flask_uploads import UploadNotAllowed

from actor_libs.decorators import limit_upload_file
from actor_libs.errors import APIException, ParameterInvalid
from app import auth, images, packages
from app.models import UploadInfo
from . import bp


@bp.route('/download')
def download_file():
    file_type = request.args.get('fileType', None, type=str)
    filename = request.args.get('filename', None, type=str)
    download_path = {
        'template': 'DOWNLOAD_TEMPLATE_EXCEL_DEST',
        'export_excel': 'EXPORT_EXCEL_PATH',
        'image': 'UPLOADED_IMAGES_DEST',
        'package': 'UPLOADED_PACKAGES_DEST'
    }
    if not file_type:
        raise ParameterInvalid(field='fileType')
    if not filename:
        raise ParameterInvalid(field='filename')
    path = current_app.config.get(download_path.get(file_type))
    return send_from_directory(path, filename)


@bp.route('/upload', methods=['POST'])
@auth.login_required(permission_required=False)
@limit_upload_file()
def upload_file():
    file_type = request.args.get('fileType', None, type=str)
    file_type_dict = {
        'package': {
            'type': 1,
            'upload_set': packages
        },
        'image': {
            'type': 2,
            'upload_set': images
        }
    }
    if file_type not in file_type_dict.keys():
        raise ParameterInvalid(field='fileType')
    try:
        unique_name = hashlib.md5((str(g.user_id) + str(time.time())).encode()).hexdigest()
        upload_set = file_type_dict.get(file_type).get('upload_set')
        request_file = request.files.get('file')
        file_name = upload_set.save(request_file, name=unique_name + '.')
        file_url = '/api/v1/download?fileType=%s&filename=%s' % (file_type, file_name)
    except UploadNotAllowed:
        raise APIException()
    request_dict = {
        'fileName': file_name,
        'displayName': request_file.filename,
        'userIntID': g.user_id,
        'fileType': file_type_dict.get(file_type).get('type')
    }
    upload_info = UploadInfo()
    created_upload = upload_info.create(request_dict)
    return jsonify({
        'name': created_upload.displayName,
        'url': file_url,
        'uploadID': created_upload.id
    }), 201
