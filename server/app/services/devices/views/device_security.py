from random import randint

from flask import g, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import (
    DataExisted, DataNotFound, ReferencedError, ResourceLimited
)
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    Cert, CertAuth, Device, MqttAcl, MqttSub, Policy, Product,
    User
)
from . import bp
from .security import create_cn, generate_cert_file
from ..schemas import (
    DeviceIdsSchema, MqttSubSchema
)


@bp.route('/devices/<int:device_id>/subscriptions')
@auth.login_required
def list_device_subs(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    sub_query = MqttSub.query.filter(MqttSub.deviceIntID == device.id)
    records = sub_query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/subscriptions', methods=['POST'])
@auth.login_required
def create_device_sub(device_id):
    request_dict = MqttSubSchema.validate_request()
    topic = request_dict.get('topic')

    device, cloud_protocol = Device.query \
        .join(Product, Product.productID == Device.productID) \
        .with_entities(Device, Product.cloudProtocol) \
        .filter(Device.id == device_id) \
        .first_or_404()
    if cloud_protocol != 1:
        raise ResourceLimited(field='cloudProtocol')

    client_uid = ':'.join([g.tenant_uid, device.productID, device.deviceID])
    query_mqtt_sub = db.session.query(MqttSub.clientID, MqttSub.topic) \
        .filter(MqttSub.clientID == client_uid)
    is_exist_sub = query_mqtt_sub.filter(MqttSub.topic == topic).first()
    sub_sum = query_mqtt_sub.all()
    if is_exist_sub:
        raise DataExisted(field='topic')
    if len(sub_sum) >= 10:
        raise ResourceLimited(field='topic')

    request_dict['clientID'] = client_uid
    request_dict['deviceIntID'] = device.id
    mqtt_sub = MqttSub()
    created_mqtt_sub = mqtt_sub.create(request_dict=request_dict)
    record = created_mqtt_sub.to_dict()
    return jsonify(record), 201


@bp.route('/devices/<int:device_id>/subscriptions', methods=['DELETE'])
@auth.login_required
def delete_device_sub(device_id):
    delete_ids = get_delete_ids()
    try:
        query_mqtt_sub = MqttSub.query \
            .filter(MqttSub.deviceIntID == device_id,
                    MqttSub.id.in_(set(delete_ids))) \
            .all()
        if len(delete_ids) != len(query_mqtt_sub):
            raise DataNotFound(field='url')

        for mqtt_sub in query_mqtt_sub:
            db.session.delete(mqtt_sub)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices/<int:device_id>/certs')
@auth.login_required
def list_device_certs(device_id):
    device = Device.query \
        .filter(Device.id == device_id) \
        .with_entities(Device.id) \
        .first_or_404()

    cert_query = Cert.query \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(CertAuth.deviceIntID == device.id) \
        .with_entities(Cert.id, Cert.createAt, Cert.name, Cert.enable)

    records = cert_query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/certs', methods=['POST'])
@auth.login_required
def bind_cert(device_id):
    request_dict = DeviceIdsSchema.validate_request()
    add_cert_ids = request_dict.get('ids')

    device_uid, product_uid = Device.query \
        .with_entities(Device.deviceID, Device.productID) \
        .filter(Device.id == device_id) \
        .first_or_404()
    client_uid = ':'.join([g.tenant_uid, product_uid, device_uid])

    exist_auth_certs = db.session.query(Cert.id) \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(Cert.id.in_(add_cert_ids),
                CertAuth.deviceIntID == device_id) \
        .all()
    exist_auth_cert_ids = [cert.id for cert in exist_auth_certs]

    diff_cert_ids = set(add_cert_ids).difference(set(exist_auth_cert_ids))
    diff_cert = Cert.query \
        .join(User, User.id == Cert.userIntID) \
        .filter(Cert.id.in_(diff_cert_ids),
                User.tenantID == g.tenant_uid) \
        .all()
    for cert in diff_cert:
        new_cert_auth = CertAuth(
            deviceIntID=device_id, CN=cert.CN,
            clientID=client_uid, enable=cert.enable
        )
        db.session.add(new_cert_auth)
    db.session.commit()
    return '', 201


@bp.route('/devices/<int:device_id>/certs', methods=['DELETE'])
@auth.login_required
def delete_device_certs(device_id):
    delete_ids = get_delete_ids()

    try:
        cert_auth_list = CertAuth.query \
            .join(Device, Device.id == CertAuth.deviceIntID) \
            .join(Cert, Cert.CN == CertAuth.CN) \
            .filter(Device.id == device_id,
                    Cert.id.in_(delete_ids)) \
            .all()
        if len(delete_ids) != len(cert_auth_list):
            raise DataNotFound(field='url')

        for cert_auth in cert_auth_list:
            db.session.delete(cert_auth)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/devices/<int:device_id>/policies')
@auth.login_required
def list_device_policies(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = Policy.query \
        .join(MqttAcl, MqttAcl.policyIntID == Policy.id) \
        .filter(MqttAcl.deviceIntID == device.id)

    records = query.pagination(code_list=['access', 'allow'])
    return jsonify(records)


@bp.route('/devices/<int:device_id>/policies', methods=['POST'])
@auth.login_required
def bind_policy(device_id):
    request_dict = DeviceIdsSchema.validate_request()
    add_policy_ids = set(request_dict.get('ids'))

    device_uid, product_uid = Device.query \
        .with_entities(Device.deviceID, Device.productID) \
        .filter(Device.id == device_id) \
        .first_or_404()

    client_uid = ':'.join([g.tenant_uid, product_uid, device_uid])

    mqtt_acl = db.session.query(MqttAcl.policyIntID) \
        .filter(MqttAcl.deviceIntID == device_id,
                MqttAcl.policyIntID.in_(add_policy_ids)) \
        .all()
    exist_acl_policy_ids = [acl.policyIntID for acl in mqtt_acl]

    diff_policy_ids = set(add_policy_ids).difference(set(exist_acl_policy_ids))
    policies = Policy.query \
        .join(User, User.id == Policy.userIntID) \
        .filter(Policy.id.in_(diff_policy_ids),
                User.tenantID == g.tenant_uid) \
        .all()

    for policy in policies:
        new_mqtt_acl = MqttAcl(
            allow=policy.allow,
            access=policy.access,
            policyIntID=policy.id,
            topic=policy.topic,
            clientID=client_uid,
            deviceIntID=device_id
        )
        db.session.add(new_mqtt_acl)
    db.session.commit()
    return '', 201


@bp.route('/devices/<int:device_id>/policies', methods=['DELETE'])
@auth.login_required
def delete_device_policies(device_id):
    delete_ids = get_delete_ids()

    try:
        mqtt_acl = MqttAcl.query \
            .filter(MqttAcl.deviceIntID == device_id,
                    MqttAcl.policyIntID.in_(delete_ids)) \
            .all()
        if len(delete_ids) != len(mqtt_acl):
            raise DataNotFound(field='url')

        for acl in mqtt_acl:
            db.session.delete(acl)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def create_and_bind_cert(created_device):
    cert_name = created_device.deviceName
    if db.session.query(func.count(Cert.id)) \
            .filter(Cert.name == cert_name).scalar():
        cert_name = random_cert_name(cert_name)
    created_cn = create_cn()
    st_private_key, st_client_cert, _ = generate_cert_file(created_cn)

    cert_request_dict = {
        'name': cert_name,
        'enable': 1,
        'key': st_private_key,
        'cert': st_client_cert,
        'CN': created_cn,
        'userIntID': g.user_id
    }
    cert = Cert()
    created_cert = cert.create(cert_request_dict, commit=False)
    client_uid = ':'.join([
        created_device.tenantID, created_device.productID,
        created_device.deviceID
    ])
    cert_auth_request_dict = {
        'deviceIntID': created_device.id,
        'CN': created_cert.CN,
        'clientID': client_uid,
        'enable': created_cert.enable
    }
    cert_auth = CertAuth()
    cert_auth.create(cert_auth_request_dict, commit=False)


def random_cert_name(original_name):
    cert_name = original_name + str(randint(1, 10000))

    if db.session.query(func.count(Cert.id)) \
            .filter(Cert.name == cert_name).scalar() > 0:
        cert_name = random_cert_name(original_name)
    return cert_name
