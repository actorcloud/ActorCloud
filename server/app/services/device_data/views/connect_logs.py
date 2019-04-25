from flask import jsonify, request
from sqlalchemy import text

from app import auth
from app.models import Device, ClientConnectLog
from . import bp


@bp.route('/device_connect_logs')
@auth.login_required
def list_device_connect_logs():
    records = ClientConnectLog.query \
        .filter(ClientConnectLog.msgTime >= text("NOW() - INTERVAL '7 DAYS'")) \
        .pagination(code_list=['connectStatus'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/connect_logs')
@auth.login_required
def view_device_connect_logs(device_id):
    device = Device.query \
        .with_entities(Device.deviceID, Device.tenantID) \
        .filter(Device.id == device_id).first_or_404()
    query = ClientConnectLog.query \
        .filter(ClientConnectLog.deviceID == device.deviceID,
                ClientConnectLog.tenantID == device.tenantID)
    if not (request.args.get('start_time') or not request.args.get('end_time')):
        # if no specified start_time or end_time, return last 7 day of data
        query = query.filter(ClientConnectLog.msgTime >= text("NOW() - INTERVAL '7 DAYS'"))
    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)
