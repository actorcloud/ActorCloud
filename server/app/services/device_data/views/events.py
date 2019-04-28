from flask import jsonify, request
from sqlalchemy import text

from actor_libs.errors import ParameterInvalid
from actor_libs.utils import validate_time_period_query
from app import auth
from app.models import (Client, DeviceEvent)
from . import bp


@bp.route('/devices/<int:client_id>/events')
@bp.route('/gateways/<int:client_id>/events')
@auth.login_required
def view_client_events(client_id):
    client = Client.query \
        .with_entities(Client.deviceID, Client.tenantID) \
        .filter(Client.id == client_id).first_or_404()
    events_query = DeviceEvent.query \
        .filter(DeviceEvent.deviceID == client.deviceID,
                DeviceEvent.tenantID == client.tenantID)

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
