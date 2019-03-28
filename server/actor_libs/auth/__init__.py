from collections import defaultdict
from functools import partial, wraps

from flask import request, g
from werkzeug.datastructures import Authorization

from .base import basic_auth, token_auth
from .permission import default_verify_permission
from ..errors import AuthFailed, PermissionDenied


__all__ = ['HttpAuth']


class HttpAuth:
    def __init__(self, custom_verify_permission=None):
        self.custom_verify_permission = custom_verify_permission

        self.schemas = {
            'basic': basic_auth,
            'token': token_auth,
        }

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
                self._verify_permission()
            return func(*args, **kwargs)

        return wrapped

    def _verify_permission(self):
        """ Verify request permission """

        if self.custom_verify_permission:
            verified_permissions = self.custom_verify_permission(verify_request=True)
        else:
            verified_permissions = default_verify_permission(
                g.role_id, g.tenant_uid,
                verify_request=True
            )
        if not verified_permissions:
            raise PermissionDenied(permissions=self.permissions())

    def permissions(self):
        """
        Returns the permission dictionary for the role of the logged-in user
        Example: {'/users': ['GET', 'POST']}
        """

        if self.custom_verify_permission:
            verified_permissions = self.custom_verify_permission()
        else:
            verified_permissions = default_verify_permission(g.role_id, g.tenant_uid)

        permission_dict = defaultdict(list)
        for resource in verified_permissions:
            if resource.method is not None:
                permission_dict[resource.url].append(resource.method)
        return permission_dict
