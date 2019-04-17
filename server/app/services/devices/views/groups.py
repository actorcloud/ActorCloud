from flask import g, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    DataExisted, DataNotFound, FormInvalid, ParameterInvalid,
    ReferencedError, ResourceLimited
)
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    Device, Group, GroupDevice, MqttSub,
    Product, ProductGroupSub, User, Client
)
from . import bp
from ..schemas import (
    DeviceIdsSchema, GroupSchema, GroupUpdateSchema, GroupSubSchema
)


@bp.route('/groups')
@auth.login_required
def list_group():
    query = db.session \
        .query(Group, Product.productName,
               func.count(GroupDevice.c.deviceIntID).label('deviceCount')) \
        .join(Product, Product.productID == Group.productID) \
        .outerjoin(GroupDevice) \
        .group_by(Group, Product.productName)

    records = query.pagination()
    return jsonify(records)


@bp.route('/groups/<int:group_id>')
@auth.login_required
def view_group(group_id):
    query = Group.query \
        .join(Product, Product.productID == Group.productID) \
        .with_entities(Group, Product.productName, Product.cloudProtocol, User.username) \
        .filter(Group.id == group_id)

    code_list = ['cloudProtocol']
    record = query.to_dict(code_list=code_list)
    return jsonify(record)


@bp.route('/groups', methods=['POST'])
@auth.login_required
def create_group():
    request_dict = GroupSchema.validate_request()

    request_dict['userIntID'] = g.user_id
    group = Group()
    new_group = group.create(request_dict)
    record = new_group.to_dict()
    return jsonify(record), 201


@bp.route('/groups/<int:group_id>', methods=['PUT'])
@auth.login_required
def update_group(group_id):
    group = Group.query.filter(Group.id == group_id).first_or_404()
    request_dict = GroupUpdateSchema.validate_request(obj=group)
    updated_group = group.update(request_dict)
    record = updated_group.to_dict()
    return jsonify(record)


@bp.route('/groups', methods=['DELETE'])
@auth.login_required
def delete_group():
    delete_ids = get_delete_ids()
    query_results = Group.query.filter(Group.id.in_(delete_ids)).many()
    try:
        for group in query_results:
            group.delete()
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/groups/<int:group_id>/devices')
@auth.login_required
def view_group_devices(group_id):
    group = Group.query \
        .with_entities(Group.groupID) \
        .filter(Group.id == group_id) \
        .first_or_404()

    group_devices = db.session.query(GroupDevice.c.deviceIntID) \
        .filter(GroupDevice.c.groupID == group.groupID).all()
    device_int_ids = [
        group_device.deviceIntID for group_device in group_devices
    ]
    query = db.session \
        .query(Device.deviceName, Device.deviceID, Device.id) \
        .filter(Device.id.in_(device_int_ids))

    records = query.pagination(code_list=['deviceTypeLabel'])
    return jsonify(records)


@bp.route('/groups/<int:group_id>/devices', methods=['POST'])
@auth.login_required
def add_group_devices(group_id):
    group = Group.query \
        .with_entities(Group.groupID, Group.productID) \
        .filter(Group.id == group_id) \
        .first_or_404()

    request_dict = DeviceIdsSchema.validate_request()
    device_ids = request_dict.get('ids')

    group_devices = db.session \
        .query(GroupDevice.c.deviceIntID) \
        .filter(GroupDevice.c.groupID == group.groupID) \
        .all()
    if len(group_devices) + len(device_ids) > 1000:
        raise ResourceLimited(field='devices')

    group_device_ids = [device_id[0] for device_id in group_devices]
    diff_device_ids = set(device_ids).difference(set(group_device_ids))
    add_query_devices = db.session.query(Device.id, Device.deviceID) \
        .filter(Product.productID == group.productID,
                Device.id.in_(diff_device_ids)) \
        .all()
    if len(add_query_devices) != len(device_ids):
        raise FormInvalid(field='ids')

    if add_query_devices:
        insert_group_device_sql = """
        INSERT INTO group_devices
        ("deviceID", "deviceIntID", "groupID", "tenantID")
        VALUES (%s, %s, %s, %s);
        """
        db.engine.execute(
            insert_group_device_sql,
            [(device.deviceID, device.id, group.groupID, g.tenant_uid)
             for device in add_query_devices]
        )

    # Update group proxy sub
    group_subs = db.session \
        .query(ProductGroupSub.topic, ProductGroupSub.qos) \
        .filter(ProductGroupSub.groupIntID == group_id) \
        .all()
    if add_query_devices and group_subs:
        group_sub_dict = dict(group_subs)
        sub_client_dict = {}
        for device in add_query_devices:
            client_uid = ':'.join(
                [g.tenant_uid, group.productID, device.deviceID]
            )
            sub_client_dict[client_uid] = device.id
        group_devices_sub(sub_client_dict, group_sub_dict)
    db.session.commit()
    return '', 201


@bp.route('/groups/<int:group_id>/devices', methods=['DELETE'])
@auth.login_required
def delete_group_devices(group_id):
    """ 中间表删除特例 """
    group = Group.query.filter(Group.id == group_id).first_or_404()
    delete_ids = get_delete_ids()
    group_devices = group.devices.filter(Client.id.in_(delete_ids)).all()
    if len(delete_ids) != len(group_devices):
        raise ParameterInvalid(field='ids')
    device_ids = [group_device.id for group_device in group_devices]
    group_subs = db.session \
        .query(ProductGroupSub.topic) \
        .filter(ProductGroupSub.groupIntID == group_id) \
        .all()
    group_topics = [group_sub.topic for group_sub in group_subs]
    device_mqtt_sub = MqttSub.query \
        .filter(MqttSub.topic.in_(group_topics),
                MqttSub.deviceIntID.in_(device_ids)).all()
    try:
        for group_device in group_devices:
            group.devices.remove(group_device)
        for mqtt_sub in device_mqtt_sub:
            db.session.delete(mqtt_sub)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/groups/<int:group_id>/subscriptions')
@auth.login_required
def list_group_subs(group_id):
    """ 分组主题订阅 """
    group = Group.query \
        .with_entities(Group.id) \
        .filter(Group.id == group_id) \
        .first_or_404()

    sub_query = ProductGroupSub.query \
        .filter(ProductGroupSub.groupIntID == group.id)
    records = sub_query.pagination()
    return jsonify(records)


@bp.route('/groups/<int:group_id>/subscriptions', methods=['POST'])
@auth.login_required
def create_group_sub(group_id):
    request_dict = GroupSubSchema.validate_request()
    topic = request_dict.get('topic')
    group, cloud_protocol = Group.query \
        .join(Product, Product.productID == Group.productID) \
        .with_entities(Group, Product.cloudProtocol) \
        .filter(Group.id == group_id) \
        .first_or_404()
    if cloud_protocol != 1:
        raise ResourceLimited(field='cloudProtocol')

    sub_topic = db.session.query(ProductGroupSub.topic) \
        .filter(ProductGroupSub.groupIntID == group.id,
                ProductGroupSub.topic == topic) \
        .first()
    if sub_topic:
        raise DataExisted(field='topic')

    product_sub = ProductGroupSub(topic=topic, groupIntID=group.id)
    db.session.add(product_sub)

    group_devices = group.devices \
        .with_entities(Client.productID, Client.id, Client.deviceID) \
        .all()
    sub_client_dict = {}
    for device in group_devices:
        client_uid = ':'.join(
            [g.tenant_uid, device.productID, device.deviceID]
        )
        sub_client_dict[client_uid] = device.id
    devices_sub_sum = db.session \
        .query(MqttSub.clientID, func.count(MqttSub.id)) \
        .filter(MqttSub.clientID.in_(sub_client_dict.keys())) \
        .group_by(MqttSub.clientID) \
        .all()
    devices_sub_sum_dict = dict(devices_sub_sum)
    devices_sub_exist = db.session.query(MqttSub.clientID) \
        .filter(MqttSub.clientID.in_(sub_client_dict.keys()),
                MqttSub.topic == topic) \
        .all()

    for client_uid, device_id in sub_client_dict.items():
        if (client_uid,) in devices_sub_exist:
            continue
        if devices_sub_sum_dict.get(client_uid, 0) >= 10:
            continue
        mqtt_sub = MqttSub(
            clientID=client_uid, topic=topic,
            qos=request_dict.get('qos', 1), deviceIntID=device_id
        )
        db.session.add(mqtt_sub)
    db.session.commit()
    record = product_sub.to_dict()
    return jsonify(record), 201


@bp.route('/groups/<int:group_id>/subscriptions', methods=['DELETE'])
@auth.login_required
def delete_group_sub(group_id):
    group = Group.query.get(group_id)
    device_ids = [
        device.id for device in group.devices.with_entities(Client.id).all()
    ]

    delete_ids = get_delete_ids()

    group_subs = db.session.query(ProductGroupSub) \
        .filter(ProductGroupSub.id.in_(delete_ids),
                ProductGroupSub.groupIntID == group.id) \
        .all()
    if len(delete_ids) != len(group_subs):
        raise DataNotFound(field='url')

    try:
        delete_topic = []
        for group_sub in group_subs:
            delete_topic.append(group_sub.topic)
            db.session.delete(group_sub)

        query_mqtt_sub = MqttSub.query \
            .filter(MqttSub.deviceIntID.in_(device_ids),
                    MqttSub.topic.in_(delete_topic)) \
            .all()
        for mqtt_sub in query_mqtt_sub:
            db.session.delete(mqtt_sub)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def group_devices_sub(sub_client_dict=None, group_sub_dict=None):
    """
    Add mqtt sub with group sub when new device added to group
    :param sub_client_dict: {'client_id': 'deviceIntID'}
    :param group_sub_dict: {'topic': 'qos'}
    """
    devices_sub_sum = db.session \
        .query(MqttSub.clientID, func.count(MqttSub.id)) \
        .filter(MqttSub.clientID.in_(sub_client_dict.keys())) \
        .group_by(MqttSub.clientID) \
        .all()
    devices_sub_sum_dict = dict(devices_sub_sum)

    devices_sub_exist = db.session.query(MqttSub.clientID, MqttSub.topic) \
        .filter(MqttSub.topic.in_(group_sub_dict.keys()),
                MqttSub.deviceIntID.in_(sub_client_dict.values())) \
        .all()
    for client_uid, device_id in sub_client_dict.items():
        if devices_sub_sum_dict.get(client_uid, 0) >= 10:
            continue
        for topic, qos in group_sub_dict.items():
            if (client_uid, topic) in devices_sub_exist:
                continue
            else:
                mqtt_sub = MqttSub(
                    clientID=client_uid, topic=topic,
                    qos=qos, deviceIntID=device_id
                )
            db.session.add(mqtt_sub)
