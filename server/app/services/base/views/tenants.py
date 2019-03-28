from flask import jsonify, g, request
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import APIException, FormInvalid, DataNotFound
from app import auth
from app.models import User, Tenant
from . import bp
from ..schemas import TenantUpdateSchema


@bp.route('/tenants')
@auth.login_required
def list_tenants():
    if g.role_id != 1:
        raise DataNotFound(field='url')

    query = db.session.query(Tenant,
                             func.coalesce(Tenant.company, User.username).label('tenantName')) \
        .outerjoin(User)

    tenant_name = request.args.get('tenantName_like')
    if tenant_name:
        query = query \
            .filter(Tenant.company.ilike(u'%{0}%'.format(tenant_name)))
        person_tenant_query = db.session \
            .query(Tenant, func.coalesce(Tenant.company, User.username).label('tenantName')) \
            .join(User, User.tenantID == Tenant.tenantID) \
            .filter(User.username.ilike(u'%{0}%'.format(tenant_name)))
        query = query.union(person_tenant_query)

    records = query.pagination(code_list=['tenantType'])
    return jsonify(records)


@bp.route('/tenants/<int:tenant_id>')
@auth.login_required
def view_tenant(tenant_id):
    if g.role_id != 1:
        raise DataNotFound(field='url')

    query = db.session.query(Tenant,
                             func.coalesce(Tenant.company, User.username).label('tenantName')) \
        .outerjoin(User) \
        .filter(Tenant.id == tenant_id)

    record = query.to_dict(code_list=['tenantType'])
    return jsonify(record)


@bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@auth.login_required
def update_tenant(tenant_id):
    if g.role_id != 1:
        raise DataNotFound(field='url')

    tenant = Tenant.filter(Tenant.id == tenant_id).first_or_404()
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    enable = request_dict.get('enable')
    if enable not in [0, 1]:
        raise FormInvalid(field='enable')

    update_dict = {'enable': enable}
    updated_tenant = tenant.update(update_dict)
    record = updated_tenant.to_dict()
    return jsonify(record)


@bp.route('/tenant_info')
@auth.login_required(permission_required=False)
def get_tenant():
    tenant = Tenant.query.filter_by(tenantID=g.tenant_uid).first_or_404()
    record = tenant.to_dict()
    record['logo'] = [record['logo']]
    record['logoDark'] = [record['logoDark']]
    return jsonify(record)


@bp.route('/tenant_info', methods=['PUT'])
@auth.login_required(permission_required=False)
def update_tenant_info():
    tenant = Tenant.query.filter_by(tenantID=g.tenant_uid).first_or_404()
    request_dict = TenantUpdateSchema.validate_request(obj=tenant)
    updated_tenant = tenant.update(request_dict)
    record = updated_tenant.to_dict()
    return jsonify(record)
