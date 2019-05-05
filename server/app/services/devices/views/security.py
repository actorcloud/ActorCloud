import os

from OpenSSL import crypto
from flask import jsonify, g, current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.errors import ReferencedError
from actor_libs.utils import get_delete_ids, generate_uuid
from app import auth
from app.models import User, Cert, Client, CertClient
from app.schemas import CertSchema, CertClientSchema
from . import bp


@bp.route('/certs')
@auth.login_required
def list_certs():
    records = Cert.query \
        .with_entities(Cert.id, Cert.createAt,
                       Cert.certName, Cert.enable) \
        .pagination()
    return jsonify(records)


@bp.route('/certs/<int:cert_id>')
@auth.login_required
def view_cert(cert_id):
    record = Cert.query.filter(Cert.id == cert_id) \
        .join(User, User.id == Cert.userIntID) \
        .with_entities(Cert, User.username.label('createUser')) \
        .to_dict()
    return jsonify(record)


@bp.route('/certs', methods=['POST'])
@auth.login_required
def create_cert():
    request_dict = CertSchema.validate_request()
    request_dict.update(generate_cert())
    cert = Cert()
    created_cert = cert.create(request_dict)
    record = created_cert.to_dict()
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
    client_count = db.session \
        .query(func.count(CertClient.c.clientIntID)) \
        .filter(CertClient.c.certIntID.in_(delete_ids)).scalar()
    if client_count > 0:
        raise ReferencedError(field='clients')
    query_results = Cert.query \
        .filter(Cert.id.in_(delete_ids)) \
        .many(allow_none=False, expect_result=len(delete_ids))
    try:
        for cert in query_results:
            db.session.delete(cert)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/certs/<int:cert_id>/clients')
@auth.login_required
def view_bind_clients(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()

    records = Client.query \
        .join(CertClient, CertClient.c.clientIntID == Client.id) \
        .filter(CertClient.c.certIntID == cert.id).pagination()
    return jsonify(records)


@bp.route('/certs/<int:cert_id>/clients', methods=['POST'])
@auth.login_required
def bind_client(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    request_dict = CertClientSchema.validate_request(obj=cert)
    add_clients = request_dict['clients']
    cert.clients.extend(add_clients)
    cert.update()
    record = {'clients': [client.id for client in add_clients]}
    return jsonify(record), 201


@bp.route('/certs/<int:cert_id>/clients', methods=['DELETE'])
@auth.login_required
def delete_cert_clients(cert_id):
    cert = Cert.query.filter(Cert.id == cert_id).first_or_404()
    clients_id = get_delete_ids()
    clients = Client.query.filter(Client.id.in_(clients_id)) \
        .many(allow_none=False, expect_result=len(clients_id))
    try:
        for client in clients:
            cert.clients.remove(client)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


def generate_cert():
    key_pair, sign_req, cert_cn = _create_cert_sign()
    filetype_pem = crypto.FILETYPE_PEM
    certs_path = current_app.config.get('CERTS_PATH')
    ca_crt_path = os.path.join(certs_path, 'actorcloud/my_ca.crt')
    ca_key_path = os.path.join(certs_path, 'actorcloud/my_ca.key')
    with open(ca_crt_path, 'r') as ca_file:
        ca_crt = crypto.load_certificate(
            filetype_pem, ca_file.read().encode('utf-8')
        )
    with open(ca_key_path, 'r', encoding='utf-8') as ca_file:
        ca_key = crypto.load_privatekey(
            filetype_pem, ca_file.read()
        )
    certificate = _create_certificate(sign_req, ca_crt, ca_key)
    issuer_private_key = crypto.dump_privatekey(
        filetype_pem, key_pair
    ).decode('utf-8')
    issuer_client_cert = crypto.dump_certificate(
        filetype_pem, certificate
    ).decode('utf-8')
    cert_info = {
        'CN': cert_cn,
        'key': issuer_private_key,
        'cert': issuer_client_cert
    }
    return cert_info


def _create_cert_sign():
    cert_cn = f"{g.tenant_uid}:{generate_uuid(size=26)}"
    # create a public/private key pair.
    key_pair = crypto.PKey()
    key_pair.generate_key(crypto.TYPE_RSA, 2048)  # TYPE_RSA, 2048 bit
    # create a certificate request.
    sign_req = crypto.X509Req()
    sign_subject = sign_req.get_subject()
    setattr(sign_subject, 'CN', cert_cn)  # set common name
    sign_req.set_pubkey(key_pair)
    sign_req.sign(key_pair, 'sha256')  # sha256 digest
    return key_pair, sign_req, cert_cn


def _create_certificate(sign_req, ca_crt, ca_key):
    serial = 0  # serial number for the certificate
    not_before = 0  # starts being valid
    not_after = 60 * 60 * 24 * 365 * 1  # stops being valid
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(not_before)
    cert.gmtime_adj_notAfter(not_after)
    cert.set_issuer(ca_crt.get_subject())
    cert.set_subject(sign_req.get_subject())
    cert.set_pubkey(sign_req.get_pubkey())
    cert.sign(ca_key, 'sha256')
    return cert
