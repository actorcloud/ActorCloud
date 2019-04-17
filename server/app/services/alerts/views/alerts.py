from flask import jsonify, request
from sqlalchemy import desc, and_
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.decorators import ip_limit
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids
from app import auth, app
from app.models import Device, CurrentAlert, HistoryAlert, BusinessRule
from . import bp
from ..schemas import CurrentAlertSchema


@bp.route('/current_alerts')
@auth.login_required
def list_current_alerts():
    query = CurrentAlert.query \
        .join(Device, and_(Device.deviceID == CurrentAlert.deviceID,
                           Device.tenantID == CurrentAlert.tenantID)) \
        .outerjoin(BusinessRule, and_(BusinessRule.id == CurrentAlert.ruleIntID,
                                      CurrentAlert.ruleIntID.isnot(None))) \
        .with_entities(CurrentAlert, Device.deviceName, BusinessRule.ruleName) \
        .order_by(desc(CurrentAlert.startTime))

    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Device.deviceName.ilike(u'%{0}%'.format(device_name)))
    records = query.pagination(code_list=['alertSeverity'])
    return jsonify(records)


@bp.route('/current_alerts/<int:alert_id>')
@auth.login_required
def view_current_alert(alert_id):
    query = CurrentAlert.query \
        .join(Device, and_(Device.deviceID == CurrentAlert.deviceID,
                           Device.tenantID == CurrentAlert.tenantID)) \
        .outerjoin(BusinessRule, and_(BusinessRule.id == CurrentAlert.ruleIntID,
                                      CurrentAlert.ruleIntID.isnot(None))) \
        .with_entities(CurrentAlert, Device.deviceName, BusinessRule.ruleName) \
        .filter(CurrentAlert.id == alert_id)

    record = query.to_dict(code_list=['alertSeverity'])
    return jsonify(record)


@bp.route('/current_alerts', methods=['POST'])
@ip_limit(allow_list=[app.config.get('STREAM_IP')])
def create_current_alert():
    request_dict = CurrentAlertSchema.validate_request()
    tenant_uid = request_dict.get('tenantID')
    device_uid = request_dict.get('deviceID')
    rule_id = request_dict.get('ruleIntID')
    current_alert = CurrentAlert.query \
        .filter(CurrentAlert.tenantID == tenant_uid,
                CurrentAlert.deviceID == device_uid,
                CurrentAlert.ruleIntID == rule_id) \
        .first()
    if current_alert:
        current_alert.alertTimes += 1
        current_alert.alertDetail = request_dict.get('alertDetail')
        current_alert.update()
    else:
        CurrentAlert().create(request_dict)
    return 'ok'


@bp.route('/current_alerts', methods=['DELETE'])
@auth.login_required
def delete_current_alerts():
    delete_ids = get_delete_ids()
    query_results = CurrentAlert.query.filter(CurrentAlert.id.in_(delete_ids)).many()
    try:
        for alert in query_results:
            db.session.delete(alert)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/history_alerts')
@auth.login_required
def list_history_alerts():
    query = HistoryAlert.query \
        .join(Device, and_(Device.deviceID == HistoryAlert.deviceID,
                           Device.tenantID == HistoryAlert.tenantID)) \
        .with_entities(HistoryAlert, Device.deviceName) \
        .order_by(desc(HistoryAlert.endTime))

    device_name = request.args.get('deviceName_like')
    if device_name:
        query = query.filter(Device.deviceName.ilike(u'%{0}%'.format(device_name)))
    records = query.pagination(code_list=['alertSeverity'])
    return jsonify(records)


@bp.route('/history_alerts/<int:alert_id>')
@auth.login_required
def view_history_alert(alert_id):
    query = HistoryAlert.query \
        .join(Device, and_(Device.deviceID == HistoryAlert.deviceID,
                           Device.tenantID == HistoryAlert.tenantID)) \
        .with_entities(HistoryAlert, Device.deviceName) \
        .filter(HistoryAlert.id == alert_id)
    record = query.to_dict(code_list=['alertSeverity'])
    return jsonify(record)


@bp.route('/history_alerts', methods=['DELETE'])
@auth.login_required
def delete_history_alerts():
    delete_ids = get_delete_ids()
    query_results = HistoryAlert.query.filter(HistoryAlert.id.in_(delete_ids)).many()
    try:
        for alert in query_results:
            db.session.delete(alert)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204
