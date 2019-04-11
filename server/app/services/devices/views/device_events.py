from datetime import datetime, timedelta

from flask import g, jsonify, request
from sqlalchemy import and_, text

from actor_libs.errors import ParameterInvalid
from actor_libs.utils import validate_time_period_query
from app import auth
from app.models import (
    Application, Device, DeviceConnectLog,
    DeviceEvent, Product,
    User, Client, DeviceControlLog
)
from . import bp


@bp.route('/device_connect_logs')
@auth.login_required
def list_device_connect_logs():
    query = DeviceConnectLog.query \
        .join(Client, and_(Client.deviceID == DeviceConnectLog.deviceID,
                           Client.tenantID == DeviceConnectLog.tenantID)) \
        .with_entities(DeviceConnectLog, Client.deviceName)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Device.productID.in_(product_ids))
    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Client.deviceName.ilike(u'%{0}%'.format(device_name)))

    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/connect_logs')
@auth.login_required
def view_device_connect_logs(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = DeviceConnectLog.query \
        .filter(DeviceConnectLog.deviceID == device.deviceID,
                DeviceConnectLog.tenantID == device.tenantID)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)


@bp.route('/device_control_logs')
@auth.login_required
def list_control_logs():
    query = DeviceControlLog.query \
        .join(User, User.id == DeviceControlLog.userIntID) \
        .join(Device, Device.id == DeviceControlLog.deviceIntID) \
        .with_entities(DeviceControlLog, Device.deviceName,
                       User.username.label('createUser'))
    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Device.productID.in_(product_ids))

    records = query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/control_logs')
@auth.login_required
def device_control_logs(device_id):
    device = Device.query.with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = DeviceControlLog.query \
        .join(User, User.id == DeviceControlLog.userIntID) \
        .with_entities(DeviceControlLog, User.username.label('createUser')) \
        .filter(DeviceControlLog.deviceIntID == device.id)
    records = query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/device_events')
@auth.login_required
def list_device_events():
    query = DeviceEvent.query \
        .join(Client, and_(Client.deviceID == DeviceEvent.deviceID,
                           Client.tenantID == DeviceEvent.tenantID)) \
        .with_entities(DeviceEvent, Client.deviceName)
    if not (request.args.get('start_time') and request.args.get('end_time')):
        date_now = datetime.now()
        last_week = date_now - timedelta(weeks=1)
        query = query.filter(DeviceConnectLog.createAt > last_week)

    if g.app_uid:
        application = Application.query \
            .filter(Application.appID == g.app_uid) \
            .first_or_404()
        product_ids = [product.productID for product in application.products]
        query = query.filter(Product.productID.in_(product_ids))
    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Client.deviceName.ilike(u'%{0}%'.format(device_name)))

    records = query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/events')
@auth.login_required
def view_device_events(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id) \
        .first_or_404()
    events_query = DeviceEvent.query \
        .filter(DeviceEvent.deviceID == device.deviceID,
                DeviceEvent.tenantID == device.tenantID)

    data_type = request.args.get('dataType', type=str)
    if data_type == 'realtime':
        events_query = events_query \
            .filter(DeviceEvent.msgTime >= text("NOW() - INTERVAL '1 DAYS'"))
    elif data_type == 'history':
        start_time, end_time = validate_time_period_query()
        events_query = events_query \
            .filter(DeviceEvent.msgTime >= start_time, DeviceEvent.msgTime <= end_time)
    else:
        raise ParameterInvalid(field='dataType')
    events_query = events_query.order_by(DeviceEvent.msgTime.desc())

    records = events_query.pagination()
    return jsonify(records)
