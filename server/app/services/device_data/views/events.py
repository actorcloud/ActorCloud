from flask import jsonify
from sqlalchemy import text, desc

from app import auth
from app.models import Device, DeviceEvent
from . import bp
from ._utils import add_time_filter


@bp.route('/devices/<int:device_id>/events')
@auth.login_required
def list_device_events(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id).first_or_404()

    events_query = DeviceEvent.query.filter(DeviceEvent.deviceID == device.deviceID)
    events_query = add_time_filter(events_query)
    records = events_query.pagination(code_list=['dataType'])

    return jsonify(records)


@bp.route('/devices/<int:device_id>/last_event')
@auth.login_required
def view_device_last_event(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(DeviceEvent.id == device_id).first_or_404()

    event = DeviceEvent.query \
        .filter_tenant(tenant_uid=device.tenantID) \
        .filter(DeviceEvent.deviceID == device.deviceID) \
        .filter(DeviceEvent.msgTime >= text("NOW() - INTERVAL '1 DAYS'")) \
        .order_by(desc(DeviceEvent.msgTime)) \
        .first()

    record = event.to_dict(code_list=['dataType']) if event else {}
    return jsonify(record)
