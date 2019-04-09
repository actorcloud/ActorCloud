from flask import request, g
from marshmallow import Schema, SchemaOpts, fields, post_load

from actor_libs.errors import APIException, FormInvalid


__all__ = ['BaseSchema']


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

    def get_request_data(self, key):
        request_data = request.get_json()
        if not request_data:
            return None
        if not request_data.get(key):
            return None
        else:
            return request_data[key]

    @post_load
    def add_tenant_info(self, data):
        if request.method != 'POST':
            return data

        data['tenantID'] = g.get('tenant_uid')
        data['userIntID'] = g.get('user_id')
        return data
