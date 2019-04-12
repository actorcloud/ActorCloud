from collections import defaultdict
from functools import partial, wraps
from typing import List

from flask import request
from werkzeug.datastructures import Authorization

from app.models import Resource
from .base import basic_auth, token_auth
from .resources import base_query_resources, parse_request_path
from ..errors import AuthFailed, PermissionDenied


__all__ = ['HttpAuth']


class HttpAuth:
    def __init__(self):
        self.schemas = {
            'basic': basic_auth,
            'token': token_auth,
        }
        self.query_resources = base_query_resources

    def get_auth(self):
        """ Support basic auth, bearer token """

        auth = request.authorization  # werkzeug parse authorization header
        if auth is None and request.headers.get('Authorization'):
            # bearer token
            try:
                auth_type, token = request.headers['Authorization'].split(None, 1)
                if isinstance(auth_type, str) and auth_type.lower() == 'bearer':
                    auth_type = 'token'
                    auth = Authorization(auth_type, {'token': token})
                else:
                    raise AuthFailed(field='headers')
            except ValueError:
                # The authorization header is either empty or has no token
                auth = None
        if auth is None and request.args.get('token'):
            auth_type = 'token'
            auth = Authorization(auth_type, {'token': request.args['token']})
        if auth is None and request.form.get('token'):
            auth_type = 'token'
            auth = Authorization(auth_type, {'token': request.form['token']})
        if auth is None:
            raise AuthFailed(field='AuthType')
        if not self.schemas.get(auth.type):
            raise AuthFailed(field='AuthType')
        return auth

    def login_required(self, func=None, *, permission_required=True):
        if func is None:
            return partial(self.login_required, permission_required=permission_required)

        @wraps(func)
        def wrapped(*args, **kwargs):
            auth = self.get_auth()
            verify_auth = self.schemas[auth.type]
            verify_status: bool = verify_auth(**auth)
            if not verify_status:
                raise AuthFailed(field='AuthFailed')
            if permission_required:
                verify_status = self._verify_request_permission()
                if not verify_status:
                    permission_dict = self._generate_permission()
                    raise PermissionDenied(permissions=permission_dict)
            return func(*args, **kwargs)

        return wrapped

    def _verify_request_permission(self) -> bool:
        """ Verify current request permission """

        verify_status = True
        request_method, request_path = parse_request_path()
        query = self.query_resources()
        request_resource = query \
            .filter(Resource.method == request_method,
                    Resource.url == request_path).first()
        if not request_resource:
            verify_status = False
        return verify_status

    def permission_resources(self, role_id: int = None, tenant_uid: str = None) -> List:
        query = self.query_resources(role_id, tenant_uid)
        all_resources = query.all()
        return all_resources

    def _generate_permission(self):
        """
        Returns the permission dictionary for the role of the logged-in user
        Example: {'/users': ['GET', 'POST']}
        """

        _permission_resources = self.permission_resources()
        permission_dict = defaultdict(list)
        for resource in _permission_resources:
            if resource.method is not None:
                permission_dict[resource.url].append(resource.method)
        return permission_dict
