import json
from json.decoder import JSONDecodeError
from marshmallow import fields, validate


__all__ = [
    'EmqField', 'EmqFloat', 'EmqEmail', 'EmqDateTime', 'EmqBool',
    'EmqList', 'EmqInteger', 'EmqDict', 'EmqString', 'EmqJson'
]


class EmqField(fields.Field):
    def __init__(self, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)


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


class EmqJson(fields.String):
    def __init__(self, *arg, **kwargs):

        fields.Field.__init__(self, *arg, **kwargs)
        self.error_messages = {
            'invalid': [u'Not a valid Json'],
            'null': [u'Fields must not be null'],
            'required': [u'Missing data for required field']
        }

    def _deserialize(self, value, attr, data):
        if self.allow_none and not value:
            return value
        elif not value:
            self.fail('null')
        elif not isinstance(value, str):
            self.fail('invalid')
        else:
            try:
                json.loads(value)
            except JSONDecodeError:
                self.fail('invalid')
        return value
