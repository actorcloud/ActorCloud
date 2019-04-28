from flask import jsonify, request
from sqlalchemy import text

from app import auth
from app.models import Client, ConnectLog
from . import bp


@bp.route('/devices/<int:client_id>/connect_logs')
@bp.route('/gateways/<int:client_id>/connect_logs')
@auth.login_required
def view_connect_logs(client_id):
    client = Client.query \
        .with_entities(Client.deviceID, Client.tenantID) \
        .filter(Client.id == client_id).first_or_404()
    query = ConnectLog.query \
        .filter(ConnectLog.deviceID == client.deviceID,
                ConnectLog.tenantID == client.tenantID)
    if not (request.args.get('start_time') or not request.args.get('end_time')):
        # if no specified start_time or end_time, return last 7 day of data
        query = query.filter(ConnectLog.msgTime >= text("NOW() - INTERVAL '7 DAYS'"))
    records = query.pagination(code_list=['connectStatus'])
    return jsonify(records)
