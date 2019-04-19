from collections import defaultdict

from flask import g, jsonify, request

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid
from app import auth
from app.models import (
    Cert, CertAuth, Client, Device, Gateway, Group,
    Lwm2mInstanceItem, Lwm2mItem, Lwm2mObject, MqttAcl,
    Policy, Product, ProductItem, GroupDevice
)
from . import bp


@bp.route('/emq_select/devices')
@auth.login_required(permission_required=False)
def list_emq_select_devices():
    """
    devices: select devices, publish
    rules: business rules
    """

    value_type = request.args.get('selectType', 'uid', type=str)
    query = Client.query \
        .join(Product, Product.productID == Client.productID)
    if value_type == 'uid':
        records = query \
            .with_entities(Client.id.label('deviceIntID'), Client.deviceName.label('label'),
                           Client.deviceID.label('value'), Product.cloudProtocol) \
            .select_options(attrs=['deviceIntID', 'cloudProtocol'])

    else:
        records = query \
            .with_entities(Client.id.label('value'), Client.deviceName.label('label'),
                           Client.deviceID, Product.cloudProtocol) \
            .select_options(attrs=['deviceID', 'cloudProtocol'])

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
            .with_entities(Client.id, Client.deviceName, Client.type,
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
                'isGateway': 1 if client.type == 2 else 0
            }
        }
        records.append(record)
    return jsonify(records)


@bp.route('/emq_select/overview/clients')
@auth.login_required(permission_required=False)
def list_overview_clients():
    if g.role_id == 1 and not g.tenant_uid:
        records = []
    else:
        records = Client.query \
            .with_entities(Client.id.label('value'), Client.deviceName.label('label'), Client.type,
                           Client.deviceID) \
            .select_options(attrs=['type', 'deviceID'])

    return jsonify(records)


@bp.route('/emq_select/publish/devices')
@auth.login_required(permission_required=False)
def list_publish_devices():
    """
    For timer task and action(location, rule_engine)
    """

    records = Client.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device.id.label('deviceIntID'), Device.deviceName.label('label'),
                       Device.deviceID.label('value'), Product.cloudProtocol) \
        .select_options(attrs=['deviceIntID', 'cloudProtocol'])

    return jsonify(records)


@bp.route('/emq_select/gateways')
@auth.login_required(permission_required=False)
def list_select_gateways():
    records = Gateway.query \
        .with_entities(Gateway.id.label('value'), Gateway.deviceName.label('label')) \
        .select_options()
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
    group_clients_query = db.session.query(GroupDevice.c.clientIntID) \
        .filter(GroupDevice.c.groupID == group.groupID) \
        .with_entities(GroupDevice.c.clientIntID).all()
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


@bp.route('/emq_select/product_items')
@auth.login_required(permission_required=False)
def list_emq_select_product_items(query):
    """
    For resources definition and business rules
    """

    product_id = request.args.get('productID', None)
    if not product_id:
        raise ParameterInvalid(field='productID')

    query = query \
        .join(Lwm2mItem, Lwm2mItem.id == ProductItem.itemIntID) \
        .filter(Lwm2mItem.itemOperations.in_(['R', 'RW']),
                ProductItem.productID == product_id) \
        .with_entities(ProductItem.id.label('value'), Lwm2mItem.itemName.label('label'),
                       Lwm2mItem.itemOperations, Lwm2mItem.itemID,
                       Lwm2mItem.objectID, Lwm2mItem.itemType)

    item_name_like = request.args.get('itemName_like')
    if item_name_like:
        query = query \
            .filter(Lwm2mItem.itemName.ilike(u'%{0}%'.format(item_name_like)))

    records = query.select_options(attrs=['itemOperations', 'itemType', 'objectID', 'itemID'])
    return jsonify(records)


@bp.route('/emq_select/group/product_items')
@auth.login_required(permission_required=False)
def list_emq_select_group_product_items(query):
    """
    [{
        "value": objectID,
        "label": objectName,
        "children":[{
            "value": itemID,
            "label": itemName,
            "objectID": objectID,
            "itemOperations": 'RW',
        }]
    }]
    """

    try:
        product_uid = request.args.get('productID', None)
    except Exception:
        raise ParameterInvalid(field='productID')
    product_items_list = query \
        .join(Lwm2mItem, Lwm2mItem.id == ProductItem.itemIntID) \
        .join(Lwm2mObject, Lwm2mObject.objectID == Lwm2mItem.objectID) \
        .join(Product, Product.productID == ProductItem.productID) \
        .filter(Lwm2mItem.itemOperations.isnot(None),
                Product.productID == product_uid) \
        .with_entities(Lwm2mObject.objectID, Lwm2mObject.objectName,
                       Lwm2mItem.itemName, Lwm2mItem.itemOperations,
                       Lwm2mItem.itemID, Lwm2mItem.objectID,
                       Lwm2mItem.itemType) \
        .all()
    # {'3':object_dict}
    object_dict_map = {}

    for item in product_items_list:
        if item.objectID in object_dict_map:
            object_dict = object_dict_map.get(item.objectID)
            item_dict = dict(
                value=item.itemID, label=item.itemName,
                itemOperations=item.itemOperations, objectID=item.objectID
            )
            object_dict['children'].append(item_dict)
        else:
            object_dict = dict(value=item.objectID, label=item.objectName, children=[])
            item_dict = dict(
                value=item.itemID, label=item.itemName,
                itemOperations=item.itemOperations, objectID=item.objectID
            )
            object_dict['children'].append(item_dict)
            object_dict_map[item.objectID] = object_dict
    records = []
    for value in object_dict_map.values():
        records.append(value)
    return jsonify(records)


@bp.route('/emq_select/lwm2m_items')
@auth.login_required(permission_required=False)
def list_emq_select_device_items(query):
    """
    [{
        "value": objectID,
        "label": objectName,
        "children":[
            "value": instanceID,
            "label": instanceID,
            "children": [{
                "value": id,
                "label": itemName,
                "itemID": itemID,
                "itemOperations": 'RW',
            }]
        ]
    }]
    For location,rules and actions
    request parameter: deviceIntID
    """

    try:
        device_id = request.args.get('deviceIntID', None)
        device_id = int(device_id)
    except Exception:
        raise ParameterInvalid(field='deviceIntID')

    lwm2m_instance_items = query \
        .join(Lwm2mItem, Lwm2mItem.id == Lwm2mInstanceItem.itemIntID) \
        .join(Lwm2mObject, Lwm2mObject.objectID == Lwm2mItem.objectID) \
        .filter(Lwm2mInstanceItem.deviceIntID == device_id) \
        .filter(Lwm2mItem.itemOperations.isnot(None)) \
        .with_entities(Lwm2mInstanceItem.id, Lwm2mInstanceItem.objectID,
                       Lwm2mInstanceItem.instanceID, Lwm2mItem.itemName,
                       Lwm2mItem.itemID, Lwm2mItem.itemOperations,
                       Lwm2mObject.objectName) \
        .all()
    # {'3':object_dict}
    object_dict_map = {}
    # {'3':{'0':instance_dict}}
    object_instance_dict = defaultdict(dict)
    for item in lwm2m_instance_items:
        # Update object
        if item.objectID in object_dict_map.keys():
            # Update instance item
            if item.instanceID in object_instance_dict.get(item.objectID).keys():
                object_dict = object_dict_map.get(item.objectID)
                item_dict = get_item_dict(item)
                instance_dict = object_instance_dict[item.objectID].get(item.instanceID)
                instance_dict['children'].append(item_dict)
                object_instance_dict[item.objectID][item.instanceID] = instance_dict
                instance_children = []
                for value in object_instance_dict.get(item.objectID).values():
                    instance_children.append(value)
                object_dict['children'] = instance_children
                object_dict_map[item.objectID] = object_dict
            else:
                # new instance item
                object_dict = object_dict_map.get(item.objectID)
                instance_dict = dict(value=item.instanceID,
                                     label=item.instanceID,
                                     children=[])
                item_dict = get_item_dict(item)
                instance_dict['children'].append(item_dict)
                object_dict['children'].append(instance_dict)
                object_instance_dict[item.objectID][item.instanceID] = instance_dict
                object_dict_map[item.objectID] = object_dict
        else:
            object_dict = dict(value=item.objectID, label=item.objectName, children=[])
            instance_dict = dict(value=item.instanceID, label=item.instanceID, children=[])
            item_dict = get_item_dict(item)
            instance_dict['children'].append(item_dict)
            object_dict['children'].append(instance_dict)
            object_instance_dict[item.objectID][item.instanceID] = instance_dict
            object_dict_map[item.objectID] = object_dict

    records = []
    for value in object_dict_map.values():
        records.append(value)
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


def get_item_dict(item):
    item_dict = dict(
        value=item.itemID,
        label=item.itemName,
        itemOperations=item.itemOperations
    )
    return item_dict
