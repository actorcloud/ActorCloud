import os
import random
import string

from OpenSSL import crypto
from flask import jsonify, g, current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import Tuple, List, Dict

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError, ParameterInvalid
from actor_libs.utils import get_delete_ids
from app import auth
from app.models import (
    User, Device, Cert, CertAuth, Policy, MqttAcl
)
from . import bp
from ..schemas import CertSchema, PolicySchema, AddDeviceSchema


@bp.route('/certs')
@auth.login_required
def list_certs():
    query = db.session.query(Cert.id, Cert.createAt, Cert.name, Cert.enable)
    records = query.pagination()
    return jsonify(records)


@bp.route('/certs/<int:cert_id>')
@auth.login_required
def view_cert(cert_id):
    cert, username = Cert.query \
        .filter(Cert.id == cert_id) \
        .with_entities(Cert, User.username) \
        .first_or_404()
    record = cert.to_dict()
    root_ca_path = os.path.join(current_app.config.get('CERTS_PATH'),
                                'actorcloud/root_ca.crt')
    with open(root_ca_path, 'r') as root_crt_file:
        st_root_cert = root_crt_file.read()
    record['createUser'] = username
    record['root'] = st_root_cert
    return jsonify(record)


@bp.route('/certs', methods=['POST'])
@auth.login_required
def create_cert():
    request_dict = CertSchema.validate_request()
    cn = create_cn()
    st_private_key, st_client_cert, cert_file_record = generate_cert_file(cn)
    request_dict['CN'] = cn
    request_dict['userIntID'] = g.user_id
    request_dict['key'] = st_private_key
    request_dict['cert'] = st_client_cert
    cert = Cert()
    record = cert.create(request_dict).to_dict()
    record.update(cert_file_record)
    return jsonify(record), 201


@bp.route('/certs/<int:cert_id>', methods=['PUT'])
@auth.login_required
def update_cert(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    request_dict = CertSchema.validate_request(obj=cert)
    updated_cert = cert.update(request_dict)
    record = updated_cert.to_dict()
    return jsonify(record)


@bp.route('/certs', methods=['DELETE'])
@auth.login_required
def delete_cert():
    delete_ids = get_delete_ids()
    device_count = db.session.query(func.count(CertAuth.deviceIntID)) \
        .join(Cert, Cert.CN == CertAuth.CN) \
        .filter(Cert.id.in_(delete_ids)) \
        .scalar()
    if device_count:
        raise ReferencedError(field='device')
    query_results = Cert.query.filter(Cert.id.in_(delete_ids)).many()
    try:
        for cert in query_results:
            db.session.delete(cert)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/certs/<int:cert_id>/devices')
@auth.login_required
def view_bind_devices(cert_id):
    query_cert_auth = Cert.query \
        .with_entities(Cert.id, CertAuth.deviceIntID) \
        .join(CertAuth, CertAuth.CN == Cert.CN) \
        .filter(Cert.id == cert_id) \
        .all()

    device_ids = [cert_auth.deviceIntID for cert_auth in query_cert_auth]

    cert_devices_query = Device.query.filter(Device.id.in_(device_ids))
    records = cert_devices_query.pagination()
    return jsonify(records)


@bp.route('/certs/<int:cert_id>/devices', methods=['POST'])
@auth.login_required
def bind_device(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    cert_add_device_id, cert_device_dict = request_add_devices()

    query_certs_auth = db.session \
        .query(CertAuth.deviceIntID) \
        .filter(CertAuth.deviceIntID.in_(cert_add_device_id),
                CertAuth.CN == cert.CN) \
        .all()
    exist_certs_auth_devices_id = [cert_auth.deviceIntID for cert_auth in query_certs_auth]

    diff_auth_devices_id = set(cert_add_device_id).difference(set(exist_certs_auth_devices_id))
    for diff_device_id in diff_auth_devices_id:
        new_cert_auth = CertAuth(deviceIntID=diff_device_id, CN=cert.CN)
        db.session.add(new_cert_auth)
    db.session.commit()
    return '', 201


@bp.route('/certs/<int:cert_id>/devices', methods=['DELETE'])
@auth.login_required
def delete_cert_devices(cert_id):
    delete_ids = get_delete_ids()
    cert_auth_list = CertAuth.query \
        .join(Cert, Cert.CN == CertAuth.CN) \
        .filter(Cert.id == cert_id,
                CertAuth.deviceIntID.in_(delete_ids)) \
        .all()
    if len(cert_auth_list) != len(delete_ids):
        raise ParameterInvalid(field='ids')

    try:
        for cert_auth in cert_auth_list:
            db.session.delete(cert_auth)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/policies')
@auth.login_required
def list_policies():
    records = Policy.query.pagination(code_list=['access', 'allow'])
    return jsonify(records)


@bp.route('/policies/<int:policy_id>')
@auth.login_required
def view_policy(policy_id):
    query = Policy.query \
        .with_entities(Policy, User.username.label('createUser')) \
        .filter(Policy.id == policy_id)

    record = query.to_dict(code_list=['access', 'allow'])
    return jsonify(record)


@bp.route('/policies', methods=['POST'])
@auth.login_required
def create_policies():
    request_dict = PolicySchema.validate_request()
    request_dict['userIntID'] = g.user_id
    policy = Policy()
    new_policy = policy.create(request_dict)
    record = new_policy.to_dict()
    return jsonify(record), 201


@bp.route('/policies/<int:policy_id>', methods=['PUT'])
@auth.login_required
def update_policy(policy_id):
    policy = Policy.query.filter(Policy.id == policy_id).first_or_404()
    request_dict = PolicySchema.validate_request(obj=policy)

    mqtt_acl = MqttAcl.query.filter(MqttAcl.policyIntID == policy_id).all()
    for acl in mqtt_acl:
        acl.access = request_dict.get('access')
        acl.allow = request_dict.get('allow')
        acl.topic = request_dict.get('topic')
    updated_policy = policy.update(request_dict)
    record = updated_policy.to_dict()
    return jsonify(record)


@bp.route('/policies', methods=['DELETE'])
@auth.login_required
def delete_policy():
    delete_ids = get_delete_ids()

    policy_device = db.session \
        .query(func.count(MqttAcl.deviceIntID)) \
        .filter(MqttAcl.policyIntID.in_(delete_ids)) \
        .scalar()
    if policy_device:
        raise ReferencedError(field='device')
    query_results = Policy.query.filter(Policy.id.in_(delete_ids)).many()
    try:
        for policy in query_results:
            db.session.delete(policy)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/policies/<int:policy_id>/devices')
@auth.login_required
def view_policy_devices(policy_id):
    query_mqtt_acl = Policy.query \
        .join(MqttAcl, MqttAcl.policyIntID == Policy.id) \
        .with_entities(Policy.id, MqttAcl.deviceIntID) \
        .filter(Policy.id == policy_id) \
        .all()

    device_ids = [mqtt_acl.deviceIntID for mqtt_acl in query_mqtt_acl]

    records = Device.query \
        .filter(Device.id.in_(device_ids)) \
        .pagination()
    return jsonify(records)


@bp.route('/policies/<int:policy_id>/devices', methods=['POST'])
@auth.login_required
def add_policy_devices(policy_id):
    policy = Policy.query.filter(Policy.id == policy_id).first_or_404()

    policy_add_devices_id, policy_device_dict = request_add_devices()
    query_mqtt_acl = db.session \
        .query(MqttAcl.deviceIntID) \
        .filter(MqttAcl.policyIntID == policy.id,
                MqttAcl.deviceIntID.in_(policy_add_devices_id)) \
        .all()
    exist_devices_id = [mqtt_acl.deviceIntID for mqtt_acl in query_mqtt_acl]

    diff_mqtt_acl_devices_id = set(policy_add_devices_id).difference(set(exist_devices_id))
    for diff_device_id in diff_mqtt_acl_devices_id:
        mqtt_acl = MqttAcl(
            allow=policy.allow, access=policy.access,
            policyIntID=policy.id, topic=policy.topic,
            clientID=policy_device_dict.get(diff_device_id),
            deviceIntID=diff_device_id
        )
        db.session.add(mqtt_acl)
    db.session.commit()
    return '', 201


@bp.route('/policies/<int:policy_id>/devices', methods=['DELETE'])
@auth.login_required
def delete_policies_devices(policy_id):
    delete_ids = get_delete_ids()
    query_mqtt_acl = MqttAcl.query \
        .filter(MqttAcl.policyIntID == policy_id,
                MqttAcl.deviceIntID.in_(delete_ids)) \
        .all()
    if len(query_mqtt_acl) != len(delete_ids):
        raise ParameterInvalid(field='ids')
    try:
        for mqtt_acl in query_mqtt_acl:
            db.session.delete(mqtt_acl)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def request_add_devices() -> Tuple[List, Dict]:
    add_devices = AddDeviceSchema.validate_request()
    add_devices_ids = set(add_devices.get('devicesIntID'))
    query_devices = db.session \
        .query(Device.id, Device.deviceID, Device.productID) \
        .filter(Device.id.in_(add_devices_ids),
                Device.tenantID == g.tenant_uid) \
        .all()
    devices_id = []
    devices_dict = {}
    for device in query_devices:
        device_id, device_uid, product_uid = device
        client_uid = ':'.join([g.tenant_uid, product_uid, device_uid])
        devices_id.append(device_id)
        devices_dict[device_id] = client_uid

    return devices_id, devices_dict


def generate_cert_file(cn: str) -> tuple:
    """
    Generate cert
    :param cn:  Common Name
    :return: key_string,cert_string,cert_file_record
    """
    key = create_key_pair(crypto.TYPE_RSA, 2048)
    req = create_cert_request(key, CN=cn)
    my_ca_crt_path = os.path.join(
        current_app.config.get('CERTS_PATH'), 'actorcloud/my_ca.crt'
    )
    with open(my_ca_crt_path, 'r') as my_ca_crt_file:
        st_issuer_cert = my_ca_crt_file.read()
        ca_cert = crypto.load_certificate(
            crypto.FILETYPE_PEM, st_issuer_cert.encode('utf-8')
        )
    my_ca_key_path = os.path.join(current_app.config.get('CERTS_PATH'),
                                  'actorcloud/my_ca.key')
    with open(my_ca_key_path, 'r') as my_ca_key_file:
        st_issuer_key = my_ca_key_file.read()
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, st_issuer_key)

    client_cert = create_certificate(
        req, (ca_cert, ca_key), 0, (0, 60 * 60 * 24 * 365 * 1)
    )

    st_private_key = crypto.dump_privatekey(
        crypto.FILETYPE_PEM, key
    ).decode('utf-8')
    st_client_cert = crypto.dump_certificate(
        crypto.FILETYPE_PEM, client_cert
    ).decode('utf-8')
    root_ca_path = os.path.join(
        current_app.config.get('CERTS_PATH'), 'actorcloud/root_ca.crt'
    )
    with open(root_ca_path, 'r') as root_crt_file:
        st_root_cert = root_crt_file.read()
    file_name = cn.split(':')[1]
    cert = {
        'fileName': '%s.crt' % file_name,
        'content': st_client_cert
    }
    key = {
        'fileName': '%s.key' % file_name,
        'content': st_private_key
    }
    root = {
        'fileName': 'root_ca.crt',
        'content': st_root_cert
    }
    cert_file_record = {
        'cert': cert,
        'key': key,
        'root': root
    }
    return st_private_key, st_client_cert, cert_file_record


def create_key_pair(create_type: str, bits: int):
    """
    Create a public/private key pair.
    :param: create_type - Key type, must be one of TYPE_RSA and TYPE_DSA
    :param: bits - Number of bits to use in the key
    :return:   The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(create_type, bits)
    return pkey


def create_cert_request(pkey, digest: str = "sha256", **name):
    """
    Create a certificate request.
    :param pkey: The key to associate with the request
    :param digest: Digestion method to use for signing, default is sha256
    :param name: The name of the subject of the request, possible arguments are:
            C     - Country name
            ST    - State or province name
            L     - Locality name
            O     - Organization name
            OU    - Organizational unit name
            CN    - Common name
            emailAddress - E-mail address
    :return: The certificate request in an X509Req object
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for key, value in name.items():
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req


def create_certificate(req, issuer_cert_key, serial, validity_period, digest: str = "sha256"):
    """
    Generate a certificate given a certificate request.
    :param req: - Certificate request to use
    :param issuer_cert_key:
        issuer_cert - The certificate of the issuer
        issuer_key  - The private key of the issuer
    :param serial: Serial number for the certificate
    :param validity_period:
        not_before  - Timestamp (relative to now) when the certificate starts being valid
        not_after   - Timestamp (relative to now) when the certifi      stops being valid
    :param digest: Digest method to use for signing, default is sha256
    :return: The signed certificate in an X509 object
    """
    issuer_cert, issuer_key = issuer_cert_key
    not_before, not_after = validity_period
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(not_before)
    cert.gmtime_adj_notAfter(not_after)
    cert.set_issuer(issuer_cert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuer_key, digest)
    return cert


def create_cn() -> str:
    random_str = ''.join(
        random.sample(string.ascii_letters + string.digits, 26)
    )
    return '%s:%s' % (g.tenant_uid, random_str)
