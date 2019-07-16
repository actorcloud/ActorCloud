import json
import os
import shutil
from os.path import expanduser
from typing import Dict, Tuple, Any, Optional

import paramiko
from flask import jsonify, g, request, current_app
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    APIException, DataNotFound, ReferencedError, ParameterInvalid, InternalError
)
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.utils import get_cwd, get_host_ip, get_delete_ids
from app import auth, logger
from app.models import DataStream, DataPoint, Product, Device, Codec, User, Tenant, DictCode
from . import bp
from ..schemas import CodeRunSchema, DecodeSchema, CodecSchema, CodecAdminSchema


@bp.route('/run_code', methods=['POST'])
@auth.login_required
def run_code():
    """
    codec api response
    {
       "error": {
          "decode:": "error message"
       },
       "output": {
          "status_code": 0,
          "result": {
             "data_type": "event",
             "data": {
                "humidity": {
                   "time": 1547660823,
                   "value": 34
                },
                "temperature": {
                   "time": 1547660823,
                   "value": -3.7
                }
             }
          }
       }
    }
    """
    request_json = CodeRunSchema.validate_request()
    analog_type = request_json.get('analogType')
    protocol = db.session.query(Product.cloudProtocol) \
        .filter(Product.productID == request_json.get('productID')) \
        .scalar()
    if protocol is None:
        raise DataNotFound(field='productID')
    request_url = f"http://{current_app.config['CODEC_NODE']}/api/v1/codec"
    with SyncHttp() as sync_http:
        response = sync_http.post(request_url, json=request_json)

    if response.responseCode != 200:
        try:
            errors = json.loads(response.responseContent)
        except Exception:
            errors = {
                'codec': response.responseContent
            }
        raise APIException(errors=errors)

    response_json = json.loads(response.responseContent)
    # return response if it has error
    if 'error' in response_json:
        return jsonify(response_json)

    output_data = response_json.get('output')
    status_code = output_data.get('status_code')
    # If status code is 1（ERROR）
    # or analog type is 2(encode)
    # return response without validate
    if status_code == 1 or analog_type == 2:
        return jsonify(response_json)

    result = output_data.get('result')
    error_dict = {}
    validate_data, validate_error = DecodeSchema().load(result)
    for key, value in validate_error.items():
        error_dict[key] = value[0][:-1]

    data_stream = DataStream.query \
        .filter(DataStream.productID == request_json.get('productID'),
                DataStream.tenantID == g.tenant_uid, DataStream.topic == request_json.get('topic'),
                DataStream.streamID == validate_data.get('stream_id')) \
        .first()
    if not data_stream:
        raise DataNotFound(field='data_stream')

    error, passed_data = validate_decode_response(data_stream, validate_data)
    error_dict.update(error)
    record = {
        'output': {
            'status_code': status_code,
            'result': passed_data
        }
    }
    if error_dict:
        record['error'] = error_dict
    return jsonify(record)


@bp.route('/codec')
@auth.login_required
def view_codec_list():
    """
    admin: codec list
    not admin: query by productID
    """
    if g.tenant_uid is None:
        query = Codec.query \
            .join(Tenant, Tenant.tenantID == Codec.tenantID) \
            .join(Product, Product.productID == Codec.productID) \
            .outerjoin(User, and_(User.tenantID == Tenant.tenantID,
                                  User.roleIntID == 3, Tenant.company.is_(None))) \
            .with_entities(Codec, Tenant.tenantType, Tenant.contactPhone, Product.productName,
                           func.coalesce(Tenant.company, User.username).label('tenantName'))
        record = query.pagination(code_list=['codeStatus', 'tenantType'])
    else:
        product_uid = request.args.get('productID', type=str)
        if product_uid is None:
            raise ParameterInvalid(field='productID')

        codec_query = Codec.query \
            .filter(Codec.productID == product_uid) \
            .with_entities(Codec, User.username) \
            .first()
        if codec_query is None:
            return ''
        else:
            codec, create_user = codec_query
            record = codec.to_dict(code_list=['codeStatus'])
            record['createUser'] = create_user
    return jsonify(record)


@bp.route('/codec/<int:codec_id>')
@auth.login_required
def view_codec(codec_id):
    codec = Codec.query.filter(Codec.id == codec_id).first_or_404()
    record = codec.to_dict(code_list=['codeStatus'])
    return jsonify(record)


@bp.route('/codec', methods=['POST'])
@auth.login_required
def create_codec():
    request_json = CodecSchema.validate_request()
    codec = Codec()
    codec.create(request_json)
    return jsonify(codec.to_dict()), 201


@bp.route('/codec/<int:codec_id>', methods=['PUT'])
@auth.login_required
def edit_codec(codec_id):
    """
    admin: review code
    not admin: update code
    """
    codec = Codec.query.filter(Codec.id == codec_id).first_or_404()
    if g.tenant_uid is None:
        request_dict = CodecAdminSchema.validate_request(obj=codec)
    else:
        request_dict = CodecSchema.validate_request(obj=codec)
        request_dict.pop('productID')
        # Re-set the code status to 1
        request_dict['codeStatus'] = 1
    updated_codec = codec.update(request_dict, commit=False)
    # Review success，copy file to EMQX
    if updated_codec.codeStatus == 2:
        copy_to_emqx(updated_codec)
    db.session.commit()
    record = updated_codec.to_dict(code_list=['codeStatus'])
    return jsonify(record)


@bp.route('/codec', methods=['DELETE'])
@auth.login_required
def delete_codec():
    delete_ids = get_delete_ids()
    query_results = Codec.query.filter(Codec.id.in_(delete_ids)).many()
    try:
        for codec in query_results:
            db.session.delete(codec)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def validate_decode_response(data_stream: DataStream, decode_data: Dict) -> Tuple[Dict, Dict]:
    """
    Validate decode data
    :param data_stream: data stream
    :param decode_data: decode response
    :return: error_dict validate_data
    """
    error_dict = {}
    data_dict = decode_data.get('data')
    # gateway
    if data_dict and is_gateway(data_dict):
        # validate gateway
        gateway_data = data_dict.get('gateway')
        error, valid_data = validate_output_data(gateway_data, data_stream, None)
        data_dict['gateway'] = valid_data
        error_dict.update(error)
        # validate sub devices
        devices_data_list = data_dict.get('devices')
        data_dict['devices'] = []
        for device_data_dict in devices_data_list:
            device_data = device_data_dict.get('data')
            device_id = device_data_dict.get('device_id')
            error, valid_data = validate_output_data(device_data, None, device_id)
            device_data_dict['data'] = valid_data
            data_dict['devices'].append(device_data_dict)
            error_dict.update(error)
        decode_data['data'] = data_dict
    elif data_dict:
        error, valid_data = validate_output_data(data_dict, data_stream, None)
        decode_data['data'] = valid_data
        error_dict.update(error)
    return error_dict, decode_data


def is_gateway(data_dict):
    has_key = all(k in data_dict.keys() for k in ("gateway", "devices"))
    return has_key and isinstance(data_dict.get('devices'), list)


def validate_output_data(data_dict: Dict, data_stream: DataStream,
                         device_uid: Optional[str]) -> Tuple[Dict, Dict]:
    """
    Validate data
    :param data_dict: data {"temperature":{"time":1547660823,"value":14},...}
    :param data_stream: data stream
    :param device_uid: deviceID
    :return: error,validate data
    """
    if device_uid:
        data_points = DataPoint.query \
            .join(Device, Device.productID == DataPoint.productID) \
            .filter(Device.deviceID == device_uid, Device.tenantID == g.tenant_uid) \
            .all()
        data_points_dict = {
            data_point.dataPointID: data_point
            for data_point in data_points
        }
    else:
        data_points_dict = {
            data_point.dataPointID: data_point
            for data_point in data_stream.dataPoints
        }
    valid_data = {}
    error_dict = {}
    for key, value_dict in data_dict.items():
        data_point = data_points_dict.get(key)
        if not data_point:
            error_dict[key] = 'Not found'
            continue
        point_type = data_point.pointDataType
        data_point_uid = data_point.dataPointID
        if not isinstance(value_dict, dict):
            error_dict[key] = 'Not a valid data format'
            continue
        value = value_dict.get('value')
        time = value_dict.get('time')
        if not isinstance(time, (int, float)):
            error_dict[data_point_uid] = 'Not a valid time'
        if not validate_data_type(point_type, value):
            error_dict[data_point_uid] = 'Not a valid value type'
            continue
        else:
            valid_data.update({data_point_uid: value_dict})

    return error_dict, valid_data


def validate_data_type(point_type: int, value: Any) -> bool:
    """
    Validate data type，1：number，2：str，3：boolean，4: datetime, 5：location
    :param point_type: data point type
    :param value: value
    :return: True if valid else False
    """
    validate_result = True
    if (point_type in (1, 4)) and not isinstance(value, (int, float)):
        validate_result = False
    elif point_type == 2 and not isinstance(value, str):
        validate_result = False
    elif point_type == 3 and not isinstance(value, bool):
        validate_result = False
    elif point_type == 5 and not isinstance(value, float):
        validate_result = False

    return validate_result


def copy_to_emqx(codec):
    code = codec.code
    product_uid = codec.productID
    protocol = db.session.query(DictCode.codeLabel) \
        .join(Product, Product.cloudProtocol == DictCode.codeValue) \
        .filter(Product.productID == codec.productID,
                DictCode.code == 'cloudProtocol') \
        .first_or_404()
    protocol = protocol[0].lower()
    name = f'{protocol}_{codec.tenantID}_{product_uid}.py'
    fpath = write_py(name, code)
    emq_nodes = current_app.config.get('EMQ_NODES')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    target_path = '/opt/emqx/data/parsers/'
    ssh_path = expanduser("~") + '/.ssh/id_rsa'
    try:
        for node in emq_nodes:
            ip = node.get('ip')
            if ip in ['127.0.0.1', get_host_ip()]:
                shutil.copy(fpath, target_path)
            else:
                ssh.connect(ip, node.get('port', 22), node.get('username'), key_filename=ssh_path,
                            timeout=3)
                sftp = ssh.open_sftp()
                sftp.put(fpath, target_path + name)
                sftp.close()
    except Exception as e:
        error = {'copy': str(e)}
        raise InternalError(errors=error)
    finally:
        ssh.close()
        os.remove(fpath)


def write_py(name, code):
    temp_dir = get_cwd() + '/_temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    fpath = os.path.join(temp_dir, name)
    with open(fpath, 'w') as f:
        f.write(code)
    return fpath
