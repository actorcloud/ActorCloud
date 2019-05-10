from flask import g, jsonify, request

from actor_libs.database.orm import db
from app import auth
from app.models import (
    Device, Group, Product, GroupDevice, Cert, CertDevice
)
from . import bp


@bp.route('/emq_select/devices')
@auth.login_required(permission_required=False)
def list_emq_select_devices():
    device_type = request.args.get('deviceType', type=int)
    query = Device.query \
        .join(Product, Product.productID == Device.productID)
    if device_type == 1:
        # end device
        query = query.filter(Device.deviceType == 1)
    elif device_type == 2:
        # gateway
        query = query.filter(Device.deviceType == 2)
    attrs = ['deviceType', 'deviceIntID', 'cloudProtocol', 'gatewayProtocol']
    records = query \
        .with_entities(Device.deviceID.label('value'),
                       Device.deviceName.label('label'),
                       Device.id.label('deviceIntID'),
                       Device.deviceType,
                       Product.cloudProtocol,
                       Product.gatewayProtocol) \
        .select_options(attrs=attrs)
    return jsonify(records)


@bp.route('/emq_select/test_center/devices')
@auth.login_required(permission_required=False)
def list_test_center_devices():
    if g.role_id == 1:
        records = []
    else:
        device_type = request.args.get('deviceType', type=int)
        query = Device.query \
            .join(Product, Product.productID == Device.productID)
        if device_type == 1:
            # end device
            query = query.filter(Device.deviceType == 1)
        elif device_type == 2:
            # gateway
            query = query.filter(Device.deviceType == 2)
        attrs = [
            'deviceID', 'deviceUsername', 'token',
            'deviceType', 'cloudProtocol', 'gatewayProtocol'
        ]
        records = query \
            .with_entities(Device.id.label('value'),
                           Device.deviceName.label('label'),
                           Device.deviceID,
                           Device.deviceUsername,
                           Device.token,
                           Device.deviceType,
                           Product.cloudProtocol,
                           Product.gatewayProtocol) \
            .select_options(attrs=attrs)
    return jsonify(records)


@bp.route('/emq_select/products')
@auth.login_required(permission_required=False)
def list_emq_select_products():
    product_type = request.args.get('productType', type=int)
    query = Product.query
    if product_type == 1:
        query = query.filter(Product.productType == 1)
    elif product_type == 2:
        query = query.filter(Product.productType == 2)
    attrs = ['productIntID', 'productType', 'cloudProtocol', 'gatewayProtocol']
    records = query \
        .with_entities(Product.productID.label('value'),
                       Product.productName.label('label'),
                       Product.id.label('productIntID'),
                       Product.productType,
                       Product.cloudProtocol,
                       Product.gatewayProtocol) \
        .select_options(attrs=attrs)
    return jsonify(records)


@bp.route('/emq_select/groups')
@auth.login_required(permission_required=False)
def list_select_groups():
    records = Group.query \
        .with_entities(Group.groupID.label('value'),
                       Group.groupName.label('label'),
                       Group.id.label('groupIntID')) \
        .select_options(attrs=['groupIntID'])
    return jsonify(records)


@bp.route('/emq_select/groups/<int:group_id>/not_joined_devices')
@auth.login_required(permission_required=False)
def group_not_joined_devices(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    group_devices_id = db.session.query(GroupDevice.c.deviceIntID) \
        .filter(GroupDevice.c.groupID == group.groupID).all()
    query = Device.query \
        .filter_tenant(tenant_uid=g.tenant_uid) \
        .filter(~Device.id.in_(group_devices_id)) \
        .with_entities(Device.id.label('value'),
                       Device.deviceName.label('label'))
    records = query.select_options()
    return jsonify(records)


@bp.route('/emq_select/certs')
@auth.login_required(permission_required=False)
def list_select_certs():
    records = Cert.query \
        .with_entities(Cert.id.label('value'),
                       Cert.certName.label('label')) \
        .select_options()
    return jsonify(records)


@bp.route('/emq_select/certs/<int:cert_id>/not_joined_devices')
@auth.login_required(permission_required=False)
def cert_not_joined_devices(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    cert_devices_id = db.session.query(CertDevice.c.deviceIntID) \
        .filter(CertDevice.c.certIntID == cert.id).all()
    query = Device.query \
        .filter_tenant(tenant_uid=g.tenant_uid) \
        .filter(~Device.id.in_(cert_devices_id), Device.authType == 2) \
        .with_entities(Device.id.label('value'),
                       Device.deviceName.label('label'))
    records = query.select_options()
    return jsonify(records)


@bp.route('/emq_select/channel_type')
@auth.login_required(permission_required=False)
def select_channel_type():
    channel_dict = {
        "COM": ["Modbus RTU"],
        "TCP": ["Modbus TCP"]
    }
    channel_select = []
    for channel_type, drive_list in channel_dict.items():
        select_data = {"label": channel_type, "value": channel_type, 'children': []}
        for drive in drive_list:
            select_data['children'].append({"label": drive, "value": drive})
        channel_select.append(select_data)
    return jsonify(channel_select)

