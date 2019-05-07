from flask import jsonify
from sqlalchemy import text, desc

from app import auth
from app.models import Client, DeviceEvent
from . import bp
from ._utils import add_time_filter


@bp.route('/devices/<int:client_id>/events')
@bp.route('/gateways/<int:client_id>/events')
@auth.login_required
def list_client_events(client_id):
    client = Client.query \
        .with_entities(Client.deviceID, Client.tenantID) \
        .filter(Client.id == client_id).first_or_404()

    events_query = DeviceEvent.query.filter(DeviceEvent.deviceID == client.deviceID)
    events_query = add_time_filter(events_query)
    records = events_query.pagination(code_list=['dataType'])

    return jsonify(records)


@bp.route('/devices/<int:client_id>/last_event')
@auth.login_required
def view_client_last_event(client_id):
    client = Client.query \
        .with_entities(Client.deviceID, Client.tenantID) \
        .filter(Client.id == client_id).first_or_404()

    event = DeviceEvent.query \
        .filter_tenant(tenant_uid=client.tenantID) \
        .filter(DeviceEvent.deviceID == client.deviceID) \
        .filter(DeviceEvent.msgTime >= text("NOW() - INTERVAL '1 DAYS'")) \
        .order_by(desc(DeviceEvent.msgTime)) \
        .first()

    record = event.to_dict(code_list=['dataType']) if event else {}
    return jsonify(record)
