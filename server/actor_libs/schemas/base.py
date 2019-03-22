from flask import request
from marshmallow import Schema, SchemaOpts, fields, validate

from actor_libs.errors import APIException, FormInvalid


__all__ = [
    'BaseSchema', 'EmqFloat', 'EmqEmail', 'EmqDateTime', 'EmqBool', 'EmqList', 'EmqInteger',
    'EmqDict', 'EmqString'
]


class CustomOptions(SchemaOpts):
    """ Override schema default options. """

    def __init__(self, meta):
        super(CustomOptions, self).__init__(meta)
        self.dateformat = '%Y-%m-%d %H:%M:%S'
        self.strict = True


class BaseSchema(Schema):
    OPTIONS_CLASS = CustomOptions

    id = fields.Int(dump_only=True)
    createAt = fields.DateTime(dump_only=True)
    updateAt = fields.DateTime(dump_only=True)

    def handle_error(self, exception, data):
        """ Log and raise our custom exception when (de)serialization fails. """
        raise FormInvalid(errors=exception.messages)

    @classmethod
    def validate_request(cls, request_dict=None, obj=None):
        request_get_json = request.get_json()
        if not request_get_json:
            raise APIException()
        if not request_dict:
            request_dict = request_get_json
        instance = cls()
        instance._obj = obj
        result = instance.load(request_dict)
        return result.data

    def _validate_obj(self, key, value):
        obj = getattr(self, '_obj', None)
        return obj and getattr(obj, key) == value

    def get_origin_obj(self, key):
        obj = getattr(self, '_obj', None)
        if obj and hasattr(obj, key):
            return getattr(obj, key)
        else:
            return None


class EmqString(fields.String):
    def __init__(self, len_min=None, len_max=None, *args, **kwargs):
        validates = []
        if 'validate' in kwargs.keys():
            validates.append(kwargs.pop('validate'))
        if len_min and len_max:
            validate_len = [validate.Length(max=len_max, min=len_min)]
        elif len_min:
            validate_len = [validate.Length(min=len_min)]
        elif len_max:
            validate_len = [validate.Length(max=len_max)]
        else:
            validate_len = [validate.Length(max=50)]
        validates.extend(validate_len)
        fields.String.__init__(self, validate=validates, *args, **kwargs)


class EmqInteger(fields.Integer):
    def __init__(self, *args, **kwargs):
        fields.Integer.__init__(self, *args, **kwargs)


class EmqDateTime(fields.DateTime):
    def __init__(self, *args, **kwargs):
        fields.DateTime.__init__(self, *args, **kwargs)


class EmqFloat(fields.Float):
    def __init__(self, *args, **kwargs):
        fields.Float.__init__(self, *args, **kwargs)


class EmqEmail(fields.Email):
    def __init__(self, *args, **kwargs):
        fields.Email.__init__(self, *args, **kwargs)


class EmqList(fields.Field):
    def __init__(self, list_type=None, *arg, **kwargs):

        fields.Field.__init__(self, *arg, **kwargs)
        self.error_messages = {
            'invalid': [u'Not a valid list'],
            'null': [u'Fields must not be null'],
            'required': [u'Missing data for required field']
        }
        self.list_type = list_type

    def _deserialize(self, value, attr, data):
        if self.allow_none:
            return value
        if not value:
            self.fail('null')
        elif isinstance(value, list):
            if isinstance(self.list_type, list):
                for item in value:
                    if not isinstance(item, self.list_type[0]):
                        self.fail('invalid')
                    elif not all(isinstance(item_value, self.list_type[1]) for item_value in item):
                        self.fail('invalid')
            elif self.list_type:
                if not all(isinstance(item, self.list_type) for item in value):
                    self.fail('invalid')
            else:
                pass
        else:
            self.fail('invalid')
        return value


class EmqDict(fields.Dict):
    def __init__(self, *args, **kwargs):
        fields.Dict.__init__(self, *args, **kwargs)


class EmqBool(fields.Bool):
    def __init__(self, *args, **kwargs):
        super(EmqBool, self).__init__(*args, **kwargs)
