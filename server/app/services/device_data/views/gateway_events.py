from flask import jsonify, request
from sqlalchemy import text, desc

from actor_libs.errors import ParameterInvalid
from actor_libs.utils import validate_time_period_query
from app import auth
from app.models import Gateway, DeviceEvent
from . import bp


@bp.route('/gateways/<int:gateway_id>/events')
@auth.login_required
def view_gateway_events(gateway_id):
    gateway = Gateway.query \
        .with_entities(Gateway.deviceID, Gateway.tenantID) \
        .filter(Gateway.id == gateway_id).first_or_404()

    events_query = DeviceEvent.query \
        .filter(DeviceEvent.deviceID == gateway.deviceID,
                DeviceEvent.tenantID == gateway.tenantID)
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
    events_query = events_query.order_by(desc(DeviceEvent.msgTime))

    records = events_query.pagination()
    return jsonify(records)
