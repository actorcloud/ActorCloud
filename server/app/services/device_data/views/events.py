from flask import jsonify

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
