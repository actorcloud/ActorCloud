import arrow
from flask import jsonify, request

from actor_libs.errors import ParameterInvalid, ResourceLimited
from app import auth
from . import bp
from ._reports_type import REPORTS_TYPE_FUNC


@bp.route('/reports')
@auth.login_required(permission_required=False)
def reports_data():
    request_args = _validate_request_args()
    reports_type = request_args['reportsType']
    reports_data_func = REPORTS_TYPE_FUNC.get(reports_type)
    if not reports_data_func:
        raise ParameterInvalid(field='reportsType')
    records = reports_data_func(request_args)
    return jsonify(records)


def _validate_request_args():
    request_args = request.args.to_dict()
    request_args = _validate_timestamp(request_args)
    return request_args


def _validate_timestamp(request_args):
    """
    Validate start_time and end_time, converting to a standard timestamp
    """

    time_unit = request_args.get('timeUnit')
    start_time = request_args.get('startTime')
    end_time = request_args.get('endTime')
    if time_unit not in ['hour', 'day', 'month']:
        raise ParameterInvalid(field='timeUnit')
    if not start_time:
        raise ParameterInvalid(field='startTime')
    if not end_time:
        raise ParameterInvalid(field='endTime')
    time_now = arrow.now()
    try:
        start_time = arrow.get(start_time)
    except Exception:
        raise ParameterInvalid(field='startTime')
    try:
        end_time = arrow.get(end_time)
    except Exception:
        raise ParameterInvalid(field='endTime')
    if start_time > time_now:
        raise ParameterInvalid(field='startTime')
    if start_time >= end_time:
        raise ParameterInvalid(field='startTime or endTime')
    if time_unit == 'hour' and (end_time - start_time).days > 31:
        raise ResourceLimited(field='hour')
    request_args['startTime'] = str(start_time)
    request_args['endTime'] = str(end_time)
    return request_args
