from flask import jsonify

from app import auth
from app.models import Device, DeviceEvent, DeviceEventLatest
from . import bp
from ._utils import validate_time_range


@bp.route('/devices/<int:device_id>/events')
@auth.login_required
def list_device_events(device_id):
    validate_time_range()
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id).first_or_404()

    events_query = DeviceEvent.query.filter(DeviceEvent.deviceID == device.deviceID)
    records = events_query.pagination(code_list=['dataType'])

    return jsonify(records)


@bp.route('/devices/<int:device_id>/last_event')
@auth.login_required
def view_device_last_event(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id).first_or_404()

    event = DeviceEventLatest.query \
        .filter_tenant(tenant_uid=device.tenantID) \
        .filter(DeviceEventLatest.deviceID == device.deviceID) \
        .first()

    record = [event.to_dict(code_list=['dataType'])] if event else []
    return jsonify(record)
