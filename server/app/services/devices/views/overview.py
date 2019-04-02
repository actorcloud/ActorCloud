import datetime
from collections import defaultdict

from flask import jsonify, g, request
from sqlalchemy import func, cast, Integer, or_

from actor_libs.cache import Cache
from actor_libs.database.orm import db
from actor_libs.database.orm.utils import filter_tag
from actor_libs.errors import ParameterInvalid
from actor_libs.utils import get_charts_config
from app import auth
from app.models import (
    User, Tenant, Device, Gateway, Group, Product,
    EmqxBillHour, DeviceCountHour, DeviceConnectLog, DeviceCountDay,
    EmqxBillDay, EmqxBillMonth, DeviceCountMonth
)
from . import bp


TIME_FORMAT = {
    'hour': "HH24:00",
    'day': "YYYY-MM-DD",
    'month': "YYYY-MM"
}


@bp.route('/overview/current_count')
@auth.login_required(permission_required=False)
def overview_count():
    start_time = datetime.datetime.now() - datetime.timedelta(hours=24)

    device_query = db.session \
        .query(Device.deviceStatus, func.count(Device.id)) \
        .group_by(Device.deviceStatus)
    gateway_query = db.session.query(func.count(Gateway.id))
    product_query = db.session.query(func.count(Product.id))
    group_query = db.session.query(func.count(Group.id))
    device_connect_query = db.session \
        .query(DeviceConnectLog.connectStatus, func.count(DeviceConnectLog.id)) \
        .filter(DeviceConnectLog.createAt > start_time,
                or_(DeviceConnectLog.connectStatus == 1,
                    DeviceConnectLog.connectStatus == 2)) \
        .group_by(DeviceConnectLog.connectStatus)

    if g.get('role_id') != 1 and g.get('tenant_uid'):
        device_query = device_query.filter(Device.tenantID == g.tenant_uid)
        device_connect_query = device_connect_query \
            .filter(DeviceConnectLog.tenantID == g.tenant_uid)
        product_query = product_query \
            .join(User, User.id == Product.userIntID) \
            .filter(User.tenantID == g.tenant_uid)
        group_query = group_query \
            .join(User, User.id == Group.userIntID) \
            .filter(User.tenantID == g.tenant_uid)
        tenant_count = None
        # TODO
        tenant_balance = db.session.query(Tenant.tenantBalance) \
            .filter(Tenant.tenantID == g.tenant_uid) \
            .scalar()
        gateway_query = gateway_query.filter(Gateway.tenantID == g.tenant_uid)
        if g.get('user_auth_type') == 2:
            device_query = filter_tag(Device, device_query)
            gateway_query = filter_tag(Gateway, gateway_query)
            device_connect_query = filter_tag(DeviceConnectLog, device_connect_query)
        gateway_count = gateway_query.scalar()
    elif g.get('consumer_id'):
        # TODO
        ...
    else:
        gateway_count = gateway_query.scalar()
        tenant_balance = None
        tenant_count = db.session.query(func.count(Tenant.tenantID)).scalar()
    device_dict = dict(device_query.all())
    device_connect_dict = dict(device_connect_query.all())
    product_count = product_query.scalar()
    group_count = group_query.scalar()
    device_count = sum(device_dict.values())

    records = {
        'current_count': {
            'devices': device_count,
            'gateways': gateway_count,
            'groups': group_count,
            'products': product_count,
            'tenants': tenant_count,
            'tenantBalance': tenant_balance,
            'status': {
                'total': device_count,
                'offline': device_dict.get(0, 0),
                'online': device_dict.get(1, 0),
                'sleep': device_dict.get(2, 0),
            },
            'connect': {
                'total': sum(device_connect_dict.values()),
                'success': device_connect_dict.get(1, 0),
                'failure': device_connect_dict.get(2, 0)
            }
        }
    }
    return jsonify(records)


@bp.route('/overview/messages_count')
@auth.login_required(permission_required=False)
def device_messages_count():
    time_unit = request.args.get('time_unit', None)
    if not TIME_FORMAT.get(time_unit):
        raise ParameterInvalid(field='time_unit')

    # Generate x-axis data(start time)
    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config.get('start_time')

    query = get_emqx_bills_count_query(time_unit, start_time)
    devices_bills = query.all()
    msg_type_dict = Cache().dict_code['msgType']
    devices_bills_dict = defaultdict(dict)
    for device_count in devices_bills:
        count_msg_type = msg_type_dict.get(device_count.msgType)
        devices_bills_dict[count_msg_type][device_count.msgTime] = device_count.msgCount

    exist_key = devices_bills_dict.keys()
    diff_key = set(msg_type_dict.values()) ^ set(exist_key)
    add_dict = {msg_type: {} for msg_type in diff_key}
    devices_bills_dict.update(add_dict)

    x_data = charts_config.get('x_data')
    record = {}
    for key, value_dict in devices_bills_dict.items():
        y_data = [value_dict.get(date) or 0 for date in x_data]
        record[key] = {
            'time': x_data,
            'value': y_data
        }

    return jsonify(record)


@bp.route('/overview/messages_flow')
@auth.login_required(permission_required=False)
def device_messages_flow():
    time_unit = request.args.get('time_unit', None)
    if not TIME_FORMAT.get(time_unit):
        raise ParameterInvalid(field='time_unit')

    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config.get('start_time')

    query = get_emqx_bills_size_query(time_unit, start_time)
    devices_bills = query.all()
    msg_type_dict = Cache().dict_code['msgType']
    devices_bills_dict = defaultdict(dict)
    for device_count in devices_bills:
        count_msg_type = msg_type_dict.get(device_count.msgType)
        devices_bills_dict[count_msg_type][device_count.msgTime] = device_count.msgSize

    exist_key = devices_bills_dict.keys()
    diff_key = set(msg_type_dict.values()) ^ set(exist_key)
    add_dict = {msg_type: {} for msg_type in diff_key}
    devices_bills_dict.update(add_dict)

    x_data = charts_config.get('x_data')
    record = {}
    for key, value_dict in devices_bills_dict.items():
        y_data = [value_dict.get(date) or 0 for date in x_data]
        record[key] = {
            'time': x_data,
            'value': y_data
        }

    return jsonify(record)


@bp.route('/overview/devices_count')
@auth.login_required(permission_required=False)
def overview_devices_count():
    time_unit = request.args.get('time_unit', None)
    if not TIME_FORMAT.get(time_unit):
        raise ParameterInvalid(field='time_unit')

    charts_config = get_charts_config(time_unit=time_unit)
    start_time = charts_config.get('start_time')

    query = get_devices_count_query(time_unit, start_time)
    devices_count = query.all()
    group_dict = dict(devices_count)
    x_data = charts_config.get('x_data')
    y_data = [group_dict.get(date) or 0 for date in x_data]
    record = {
        'time': x_data,
        'value': y_data
    }
    return jsonify(record)


def get_emqx_bills_count_query(time_unit, start_time):
    unit_model_dict = {
        'hour': EmqxBillHour,
        'day': EmqxBillDay,
        'month': EmqxBillMonth,
    }

    model = unit_model_dict.get(time_unit).get('model')
    time_format = unit_model_dict.get(time_unit).get('format')

    if g.role_id != 1:
        query = db.session \
            .query(func.to_char(model.countTime, time_format).label('msgTime'),
                   model.msgCount, model.msgType) \
            .filter(model.tenantID == g.tenant_uid) \
            .order_by(func.to_char(model.countTime, time_format))
    else:
        # admin
        query = db.session \
            .query(func.to_char(model.countTime,
                                time_format).label('msgTime'),
                   func.sum(model.msgCount).label('msgCount'), model.msgType) \
            .group_by(func.to_char(model.countTime,
                                   time_format).label('msgTime'),
                      model.msgType) \
            .order_by(func.to_char(model.countTime, time_format))
    query = query.filter(model.countTime > start_time)
    return query


def get_emqx_bills_size_query(time_unit, start_time):
    unit_model_dict = {
        'hour': EmqxBillHour,
        'day': EmqxBillDay,
        'month': EmqxBillMonth,
    }
    model = unit_model_dict.get(time_unit)
    time_format = TIME_FORMAT.get(time_unit)

    if g.role_id != 1:
        query = db.session \
            .query(func.to_char(model.countTime, time_format).label('msgTime'),
                   cast(model.msgSize / 1024, Integer).label('msgSize'),
                   model.msgType) \
            .filter(model.tenantID == g.tenant_uid) \
            .order_by(func.to_char(model.countTime, time_format))
    else:
        query = db.session \
            .query(func.to_char(model.countTime, time_format).label('msgTime'),
                   cast(func.sum(model.msgSize) / 1024, Integer).label('msgSize'),
                   model.msgType) \
            .group_by(func.to_char(model.countTime, time_format).label('msgTime'),
                      model.msgType) \
            .order_by(func.to_char(model.countTime, time_format))
    query = query.filter(model.countTime > start_time)
    return query


def get_devices_count_query(time_unit, start_time):
    unit_model_dict = {
        'hour': DeviceCountHour,
        'day': DeviceCountDay,
        'month': DeviceCountMonth,
    }
    model = unit_model_dict.get(time_unit)
    time_format = TIME_FORMAT.get(time_unit)

    if g.role_id != 1:
        query = db.session \
            .query(func.to_char(model.countTime, time_format),
                   model.deviceCount) \
            .filter(model.tenantID == g.tenant_uid) \
            .order_by(func.to_char(model.countTime, time_format))
    else:
        query = db.session \
            .query(func.to_char(model.countTime, time_format),
                   func.sum(model.deviceCount)) \
            .group_by(func.to_char(model.countTime, time_format)) \
            .order_by(func.to_char(model.countTime, time_format))
    query = query.filter(model.countTime > start_time)
    return query
