import re
from typing import Tuple, AnyStr

from flask import request, g
from sqlalchemy import or_

from app.models import Resource, Permission
from ..errors import AuthFailed


__all__ = ['base_query_resources', 'parse_request_path']


def base_query_resources(role_id: int = None, tenant_uid: str = None):
    """ Resource query filtering admin and personal user """

    role_id: int = role_id if role_id else g.get('role_id')
    tenant_uid: str = tenant_uid if tenant_uid else g.get('tenant_uid')

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
    return query


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
