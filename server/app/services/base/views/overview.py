from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from flask import g, request, jsonify
from sqlalchemy import func, cast, Integer

from actor_libs.cache import Cache
from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from actor_libs.utils import get_charts_config
from app import auth
from app.models import (
    Client, Device, Gateway, Product, Group, ClientConnectLog,
    DeviceCountHour, DeviceCountDay, DeviceCountMonth,
    EmqxBillHour, EmqxBillDay, EmqxBillMonth
)
from . import bp


@bp.route('/overview/current_count')
@auth.login_required(permission_required=False)
def overview_count():
    online_status, connect_status = _overview_status()
    records = {
        'current_count': {
            'devices': _query_object_count(Device),
            'gateways': _query_object_count(Gateway),
            'groups': _query_object_count(Group),
            'products': _query_object_count(Product),
            'status': online_status,
            'connect': connect_status
        }
    }
    return jsonify(records)


@bp.route('/overview/devices_count')
@auth.login_required(permission_required=False)
def overview_devices_count():
    time_unit_models = {
        'hour': DeviceCountHour, 'day': DeviceCountDay, 'month': DeviceCountMonth
    }
    time_unit, time_format = _validate_time_unit()
    model = time_unit_models[time_unit]
    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config['start_time']
    x_data = charts_config['x_data']

    # Query different models according to time unit
    time_devices_count = db.session \
        .query(func.to_char(model.countTime, time_format),
               func.sum(model.deviceCount)) \
        .filter(model.countTime > start_time) \
        .group_by(func.to_char(model.countTime, time_format)) \
        .order_by(func.to_char(model.countTime, time_format)).all()
    devices_count_dict = dict(time_devices_count)
    records = {
        'time': x_data,
        'value': [devices_count_dict.get(date, 0) for date in x_data]
    }
    return jsonify(records)


@bp.route('/overview/messages_count')
@auth.login_required(permission_required=False)
def overview_messages_count():
    time_unit_models = {
        'hour': EmqxBillHour, 'day': EmqxBillDay, 'month': EmqxBillMonth
    }
    time_unit, time_format = _validate_time_unit()
    model = time_unit_models[time_unit]
    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config['start_time']
    x_data = charts_config['x_data']
    # Query different models according to time unit
    time_messages_count = db.session \
        .query(func.to_char(model.countTime, time_format).label('msgTime'),
               model.msgType, func.sum(model.msgCount)) \
        .filter_tenant(tenant_uid=g.tenant_uid) \
        .filter(model.countTime > start_time) \
        .group_by(func.to_char(model.countTime, time_format), model.msgType) \
        .order_by(func.to_char(model.countTime, time_format)).all()
    records = _convert_query_message(time_messages_count, x_data)
    return jsonify(records)


@bp.route('/overview/messages_flow')
@auth.login_required(permission_required=False)
def overview_messages_flow():
    time_unit_models = {
        'hour': EmqxBillHour, 'day': EmqxBillDay, 'month': EmqxBillMonth
    }
    time_unit, time_format = _validate_time_unit()
    model = time_unit_models[time_unit]
    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config['start_time']
    x_data = charts_config['x_data']
    # Query different models according to time unit
    time_messages_flow = db.session \
        .query(func.to_char(model.countTime, time_format).label('msgTime'),
               model.msgType,
               cast(func.sum(model.msgSize) / 1024, Integer)) \
        .filter_tenant(tenant_uid=g.tenant_uid) \
        .filter(model.countTime > start_time) \
        .group_by(func.to_char(model.countTime, time_format), model.msgType) \
        .order_by(func.to_char(model.countTime, time_format)).all()
    records = _convert_query_message(time_messages_flow, x_data)
    return jsonify(records)


def _query_object_count(model) -> int:
    tenant_uid = g.tenant_uid
    object_count = db.session.query(func.count(model.id)) \
        .filter_tenant(tenant_uid=tenant_uid).scalar()
    return object_count


def _overview_status() -> Tuple[Dict, Dict]:
    start_time = datetime.now() - timedelta(hours=24)
    tenant_uid = g.tenant_uid
    query_online = db.session \
        .query(Client.deviceStatus, func.count(Client.id)) \
        .filter_tenant(tenant_uid=tenant_uid) \
        .group_by(Client.deviceStatus).all()
    query_connect = db.session \
        .query(ClientConnectLog.connectStatus, func.count(ClientConnectLog.msgTime)) \
        .filter_tenant(tenant_uid=tenant_uid) \
        .filter(ClientConnectLog.msgTime > start_time)\
        .group_by(ClientConnectLog.connectStatus).all()
    online_dict, connect_dict = dict(query_online), dict(query_connect)
    online_status = {
        'offline': online_dict.get(0, 0),
        'online': online_dict.get(1, 0),
        'sleep': online_dict.get(2, 0),
    }
    connect_status = {
        'success': connect_dict.get(1, 0),
        'failed': connect_dict.get(2, 0),
        'authFailed': connect_dict.get(3, 0)
    }
    online_status['total'] = sum(online_status.values())
    connect_status['total'] = sum(connect_status.values())
    return online_status, connect_status


def _validate_time_unit():
    time_format_dict = {
        'hour': "HH24:00", 'day': "YYYY-MM-DD", 'month': "YYYY-MM"
    }
    time_unit = request.args.get('time_unit', type=str)
    if not time_format_dict.get(time_unit):
        raise ParameterInvalid(field='time_unit')
    time_format = time_format_dict.get(time_unit)
    return time_unit, time_format


def _convert_query_message(query_results, x_data):
    message_type_dict = defaultdict(dict)
    for message in query_results:
        msg_type, msg_type, msg_type = message
        message_type_dict[msg_type][msg_type] = msg_type
    msg_types: List[int] = list(Cache().dict_code['msgType'].keys())
    records = {}
    query_types = []
    for msg_type, msg_dict in message_type_dict.items():
        y_data = [msg_dict.get(date, 0) for date in x_data]
        records[msg_type] = {'time': x_data, 'value': y_data}
        query_types.append(msg_type)
    defect_types = set(msg_types) ^ set(query_types)
    for defect_type in defect_types:
        records[defect_type] = {'time': x_data, 'value': [0] * len(x_data)}
    return records
