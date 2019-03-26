import re
from typing import List, Tuple, AnyStr

from flask import request, g
from sqlalchemy import or_

from app.models import Resource, Permission
from ..errors import AuthFailed


__all__ = ['default_verify_permission', 'parse_request_path']


def default_verify_permission(verify_request: bool = False) -> List:
    permission_resources = _query_resources(verify_request)
    return permission_resources


def _query_resources(verify_request: bool) -> List:
    """ Resource query filtering admin and personal user """

    role_id: int = g.get('role_id')
    tenant_uid: str = g.get('tenant_uid')
    if not role_id or not tenant_uid:
        raise AuthFailed()

    query = Resource.query \
        .join(Permission, Permission.resourceIntID == Resource.id) \
        .filter(Resource.enable == 1)
    if role_id == 1 and not tenant_uid:
        # admin user
        query = query.filter(or_(Resource.method.is_(None), Permission.roleIntID == 1))
    elif role_id != 1 and tenant_uid:
        # personal user
        query = query.filter(Permission.roleIntID == role_id)
    else:
        raise AuthFailed()
    if verify_request:
        request_method, request_path = parse_request_path()
        query_result = query.filter(Resource.method == request_method,
                                    Resource.url == request_path).first()
        resources = [query_result] if query_result else []
    else:
        resources = query.all()
    return resources


def parse_request_path() -> Tuple[AnyStr, AnyStr]:
    """ parse request path """

    request_method = request.method
    request_path = re.sub(r'/api/v\d+', '', request.path)  # remove /api/v*
    request_path = re.sub(r'/\d+', '/:id', request_path)  # replace int args to :id

    if request_method == 'GET' and ':id' in request_path:
        # GET method remove ':id' after: devices/:id -> /devices, /devices/:id/events -> /devices
        request_path = re.sub(r'/:id/*\w*$', '', request_path)
    elif request_method in ('POST', 'DELETE', 'PUT') and '/:id/' in request_path:
        request_method = 'PUT'
        request_path = re.sub(r'/:id/\w+$', r'/:id', request_path)
    return request_method, request_path
