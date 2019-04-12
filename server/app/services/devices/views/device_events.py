from flask import g, jsonify

from app import auth
from app.models import Application, Device, User, DeviceControlLog

from . import bp


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
    records = query.paginate(code_list=['publishStatus'])
    return jsonify(records)
