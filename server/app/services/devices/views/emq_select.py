from flask import g, jsonify, request

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from app import auth
from app.models import (
    Cert, CertAuth, Client, Device, Gateway, Group,
    MqttAcl, Policy, Product, GroupClient
)
from . import bp


@bp.route('/emq_select/clients')
@auth.login_required(permission_required=False)
def list_overview_clients():
    records = Client.query \
        .join(Product, Product.productID == Client.productID) \
        .with_entities(Client.deviceID.label('value'),
                       Client.deviceName.label('label'),
                       Product.cloudProtocol,
                       Client.clientType, Client.id.label('clientIntID')) \
        .select_options(attrs=['clientType', 'cloudProtocol', 'clientIntID'])
    return jsonify(records)


@bp.route('/emq_select/devices')
@auth.login_required(permission_required=False)
def list_emq_select_devices():
    records = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device.deviceID.label('value'),
                       Device.deviceName.label('label'),
                       Device.id.label('deviceIntID'),
                       Product.cloudProtocol) \
        .select_options(attrs=['deviceIntID', 'cloudProtocol'])
    return jsonify(records)


@bp.route('/emq_select/gateways')
@auth.login_required(permission_required=False)
def list_emq_select_gateways():
    records = Gateway.query \
        .join(Product, Product.productID == Gateway.productID) \
        .with_entities(Gateway.deviceID.label('value'),
                       Gateway.deviceName.label('label'),
                       Gateway.id.label('gatewayIntID'),
                       Gateway.cloudProtocol) \
        .select_options(attrs=['gatewayIntID', 'cloudProtocol'])
    return jsonify(records)


@bp.route('/emq_select/test_center/devices')
@auth.login_required(permission_required=False)
def list_test_center_devices():
    """ test center -> CoAP clients """

    cloud_protocol = request.args.get('cloudProtocol', type=str)
    cloud_protocol_dict = {'MQTT': 1, 'CoAP': 2}

    if g.role_id == 1 and not g.tenant_uid:
        records = []
    elif cloud_protocol and cloud_protocol_dict.get(cloud_protocol):
        cloud_protocol_value = cloud_protocol_dict.get(cloud_protocol)
        records = Client.query \
            .join(Product, Product.productID == Device.productID) \
            .filter(Product.cloudProtocol == cloud_protocol_value) \
            .with_entities(Device.id.label('value'), Device.deviceName.label('label'),
                           Device.token, Device.deviceID, Device.deviceUsername) \
            .select_options(attrs=['token', 'deviceID', 'deviceUsername'])
    else:
        records = []

    return jsonify(records)


@bp.route('/emq_select/test_center/clients')
@auth.login_required(permission_required=False)
def list_test_center_clients():
    """ test center -> MQTT clients """

    if g.role_id == 1 and not g.tenant_uid:
        client_list = []
    else:
        client_list = Client.query \
            .with_entities(Client.id, Client.deviceName, Client.clientType,
                           Client.deviceID, Client.deviceUsername, Client.token) \
            .many()

    records = []
    for client in client_list:
        record = {
            'value': client.id,
            'label': client.deviceName,
            'attr': {
                'deviceID': client.deviceID,
                'deviceUsername': client.deviceUsername,
                'token': client.token,
                'isGateway': 1 if Client.clientType == 2 else 0
            }
        }
        records.append(record)
    return jsonify(records)


@bp.route('/emq_select/products')
@auth.login_required(permission_required=False)
def list_emq_select_products():
    product_type = request.args.get('productType', type=int)
    if product_type is not None and product_type not in [1, 2]:
        raise ParameterInvalid(field='productType')
    query = Product.query

    if product_type:
        query = query.filter(Product.productType == product_type)
    records = query \
        .with_entities(Product.productID.label('value'), Product.productName.label('label'),
                       Product.cloudProtocol, Product.id.label('productIntID'),
                       Product.gatewayProtocol) \
        .select_options(attrs=['cloudProtocol', 'productIntID', 'gatewayProtocol'])

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


@bp.route('/emq_select/groups/<int:group_id>/not_joined_clients')
@auth.login_required(permission_required=False)
def group_not_joined_clients(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    group_clients_query = db.session.query(GroupClient.c.clientIntID) \
        .filter(GroupClient.c.groupID == group.groupID) \
        .with_entities(GroupClient.c.clientIntID).all()
    group_clients_id = [group_clients[0] for group_clients in group_clients_query]
    query = Client.query \
        .filter_tenant(tenant_uid=g.tenant_uid) \
        .filter(~Client.id.in_(group_clients_id)) \
        .with_entities(Client.id.label('value'), Client.deviceName.label('label'))
    records = query.select_options()
    return jsonify(records)


@bp.route('/emq_select/certs/<int:cert_id>/not_joined_devices')
@auth.login_required(permission_required=False)
def cert_not_joined_devices(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    query_cert_auth = db.session.query(CertAuth.deviceIntID) \
        .filter(CertAuth.CN == cert.CN) \
        .all()
    exist_id_devices = [cert_auth.deviceIntID for cert_auth in query_cert_auth]

    query = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .filter(~Device.id.in_(exist_id_devices))

    device_name = request.args.get('deviceName_like', None)
    product_name = request.args.get('productName_like', None)
    group_name = request.args.get('groupName_like', None)
    if device_name:
        query = query \
            .filter(Device.deviceName.ilike(u'%{0}%'.format(device_name))) \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    elif product_name:
        query = query \
            .filter(Product.productName.ilike(u'%{0}%'.format(product_name))) \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    elif group_name:
        query = query.join(Group, Group.productID == Product.productID) \
            .filter(Group.groupName.ilike(u'%{0}%'.format(group_name))) \
            .with_entities(Device.id, Device.deviceName,
                           Product.productName, Group.groupName)
    else:
        query = query \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    records = query.pagination()
    return jsonify(records)


@bp.route('/emq_select/devices/<int:device_id>/not_joined_certs')
@auth.login_required(permission_required=False)
def cert_not_joined_certs(device_id):
    if not g.tenant_uid:
        return jsonify([])

    device = db.session.query(Device.id) \
        .filter(Device.id == device_id,
                Device.tenantID == g.tenant_uid) \
        .first_or_404()
    exist_auth_certs = db.session.query(Cert.id) \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(CertAuth.deviceIntID == device_id) \
        .all()

    exist_id_certs = [cert.id for cert in exist_auth_certs]

    records = Cert.query \
        .filter(~Cert.id.in_(exist_id_certs)) \
        .with_entities(Cert.id.label('value'), Cert.name.label('label')) \
        .select_options()
    return jsonify(records)


@bp.route('/emq_select/policies/<int:policy_id>/not_joined_devices')
@auth.login_required(permission_required=False)
def policies_not_joined_devices(policy_id):
    policy = Policy.query.filter(Policy.id == policy_id).first_or_404()

    query_mqtt_acl = db.session.query(MqttAcl.deviceIntID) \
        .filter(MqttAcl.policyIntID == policy.id) \
        .all()
    exist_id_devices = [mqtt_acl.deviceIntID for mqtt_acl in query_mqtt_acl]

    query = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .filter(~Device.id.in_(exist_id_devices))

    device_name = request.args.get('deviceName_like', None)
    product_name = request.args.get('productName_like', None)
    group_name = request.args.get('groupName_like', None)
    if device_name:
        query = query \
            .filter(Device.deviceName.ilike(u'%{0}%'.format(device_name))) \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    elif product_name:
        query = query \
            .filter(Product.productName.ilike(u'%{0}%'.format(product_name))) \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    elif group_name:
        query = query.join(Group, Group.productID == Product.productID) \
            .filter(Group.groupName.ilike(u'%{0}%'.format(group_name))) \
            .with_entities(Device.id, Device.deviceName,
                           Product.productName, Group.groupName)
    else:
        query = query \
            .with_entities(Device.id, Device.deviceName, Product.productName)
    records = query.pagination()
    return jsonify(records)


@bp.route('/emq_select/devices/<int:device_id>/not_joined_policies')
@auth.login_required(permission_required=False)
def cert_not_joined_policies(device_id):
    if not g.tenant_uid:
        return jsonify([])

    db.session.query(Device.id) \
        .filter(Device.id == device_id,
                Device.tenantID == g.tenant_uid) \
        .first_or_404()
    exist_mqtt_acl = db.session.query(MqttAcl.policyIntID) \
        .filter(MqttAcl.deviceIntID == device_id) \
        .all()

    exist_id_acl = [acl.policyIntID for acl in exist_mqtt_acl]
    records = Policy.query \
        .filter(~Policy.id.in_(exist_id_acl)) \
        .with_entities(Policy.id.label('value'), Policy.name.label('label')) \
        .select_options()
    return jsonify(records)


@bp.route('/emq_select/channel_select')
@auth.login_required(permission_required=False)
def get_channel_select():
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

