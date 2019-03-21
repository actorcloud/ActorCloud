# coding: utf-8

import ujson
from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type


class APIException(HTTPException):
    code = 400
    error_code = 'BAD_REQUEST'
    message = 'Bad request'

    def __init__(self, field=None, errors=None):
        self.field = field
        if errors and not isinstance(errors, dict):
            raise TypeError('errors parameter must be dict')
        else:
            self.errors = errors
        super(APIException, self).__init__()

    def get_body(self, environ=None):
        error_body = {
            'errorCode': self.error_code,
            'message': self.message
        }
        if self.field:
            errors = {self.field: self.message}
            error_body['errors'] = errors
        if self.errors:
            for key, value in list(self.errors.items()):
                if isinstance(value, list) and value:
                    new_message = value[0]
                    # Delete the period in the marshmallow standard error
                    if new_message.endswith('.'):
                        new_message = new_message[:-1]
                    self.errors[key] = new_message
            error_body['errors'] = self.errors
        record = ujson.dumps(error_body)
        return text_type(record)

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]


class ReferencedError(APIException):
    """
    Referenced by other resources when the resource is deleted
    """
    code = 400
    error_code = 'REFERENCED_ERROR'
    message = 'Referenced error'


class ParameterInvalid(APIException):
    """
    Get request parameter error
    """
    code = 400
    error_code = 'PARAMETER_INVALID'
    message = 'Request args is invalid'


class DataExisted(APIException):
    code = 400
    error_code = 'DATA_EXISTED'
    message = 'Data has exist'


class AttributeUndefined(APIException):
    code = 400
    error_code = 'AttributeUndefined'
    message = 'attribute undefined'


class FormInvalid(APIException):
    """
    Form validation failed
    """
    code = 422
    error_code = 'FORM_INVALID'
    message = 'Invalid value'


class DataNotFound(APIException):
    """
    Request data or url does not exist
    """
    code = 404
    error_code = 'DATA_NOT_FOUND'
    message = 'Not found'


class LoginRequired(APIException):
    code = 401
    error_code = 'LOGIN_REQUIRED'
    message = 'Please login first'

    def get_headers(self, environ=None):
        return [
            ('Content-Type', 'application/json'),
            ('WWW-Authenticate', 'xBasic realm="Authentication Required"')
        ]


class AuthFailed(APIException):
    code = 401
    error_code = 'AUTH_FAILED'
    message = 'Auth failed'


class PermissionDenied(APIException):
    code = 403
    error_code = 'PERMISSION_DENIED'
    message = 'You have no permission to operate'

    def __init__(self, permissions=None):
        self.permissions = permissions if permissions else {}
        super(PermissionDenied, self).__init__()

    def get_body(self, environ=None):
        error_body = {
            'errorCode': self.error_code,
            'message': self.message,
            'errors': 'permission denied',
            'permissions': self.permissions
        }
        return text_type(ujson.dumps(error_body))


class ResourceLimited(APIException):
    code = 403
    error_code = 'RESOURCE_LIMITED'
    message = 'Resource limited'


class InternalError(APIException):
    code = 500
    error_code = 'INTERNAL_ERROR'
    message = 'Internal server error'
