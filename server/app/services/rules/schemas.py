import hashlib
import json
import random
import string
import time

from flask import g
from marshmallow import (
    validates, pre_load, fields, validates_schema, post_dump, validate, ValidationError
)
from marshmallow.validate import OneOf

from actor_libs.database.orm import db
from actor_libs.emqx.publish.schemas import PublishSchema
from actor_libs.errors import DataExisted, DataNotFound, FormInvalid
from actor_libs.http_tools.sync_http import SyncHttp
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger, EmqDict, EmqList
)
from actor_libs.utils import generate_uuid
from app.models import (
    Product, Rule, Device, Action, DataStream
)


__all__ = [
    'RuleSchema', 'ActionSchema', 'AlertActionSchema', 'UpdateRuleSchema',
    'EmailActionSchema', 'PublishActionSchema', 'MqttActionSchema', 'WebhookActionSchema'
]


class ActionSchema(BaseSchema):
    actionName = EmqString(required=True)
    actionType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4, 5]))
    config = EmqDict(required=True)
    description = EmqString(allow_none=True)
    userIntID = EmqInteger(dump_only=True)
    tenantID = EmqString(dump_only=True)

    @validates('actionName')
    def name_is_exist(self, value):
        if self._validate_obj('actionName', value):
            return

        query = db.session.query(Action.actionName) \
            .filter(Action.tenantID == g.tenant_uid,
                    Action.actionName == value).first()
        if query:
            raise DataExisted(field='actionName')

    @pre_load
    def restore_config(self, data):
        action_type = data.get('actionType')
        config_dict = data.get('config')
        if config_dict is None:
            return data
        if action_type == 1:
            AlertActionSchema().validate(config_dict)
        if action_type == 2:
            EmailActionSchema().validate(config_dict)
        elif action_type == 3:
            WebhookActionSchema().validate(config_dict)
        elif action_type == 4:
            # We need the config data after load
            data['config'] = PublishActionSchema().load(config_dict).data
        elif action_type == 5:
            MqttActionSchema().validate(config_dict)
        return data


class FromTopicSchema(BaseSchema):
    productID = EmqString(required=True)
    deviceID = EmqString(required=True)
    topic = EmqString(required=True)

    @validates_schema
    def validate_from(self, data):
        product_uid = data.get('productID')
        product = db.session \
            .query(Product.cloudProtocol) \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.productID == product_uid) \
            .first()
        if not product:
            raise DataNotFound(field='productID')

        device_uid = data.get('deviceID')
        # device_uid can be '+' or deviceID of device
        if device_uid != '+':
            device = db.session \
                .query(Device.id) \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(Device.productID == product_uid, Device.deviceID == device_uid) \
                .first()
            if not device:
                raise DataNotFound(field='deviceID')

        topic = data.get('topic')
        # If the protocol is LwM2M,the fixed value of topic is 'ad/#'
        if product.cloudProtocol == 3 and topic != 'ad/#':
            raise DataNotFound(field='topic')
        else:
            data_stream = db.session \
                .query(DataStream.topic) \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(DataStream.productID == product_uid, DataStream.topic == topic) \
                .first()
            if not data_stream:
                raise DataNotFound(field='topic')

    @post_dump
    def query_name(self, data):
        product_uid = data.get('productID')
        product = db.session \
            .query(Product.productName) \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Product.productID == product_uid) \
            .first()
        data['productName'] = product.productName if product else None
        device_uid = data.get('deviceID')
        if device_uid != '+':
            device = db.session \
                .query(Device.deviceName) \
                .filter_tenant(tenant_uid=g.tenant_uid) \
                .filter(Device.productID == product_uid, Device.deviceID == device_uid) \
                .first()
            data['deviceName'] = device.deviceName if device else None

        return data


class ScopeDataSchema(BaseSchema):
    devices = EmqList(required=True, list_type=str)
    scope = EmqString(required=True, len_max=1000)
    scopeType = EmqInteger()

    @validates('devices')
    def validate_devices(self, value):
        devices_count = Device.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Device.deviceID.in_(set(value))) \
            .count()
        if devices_count != len(value):
            raise DataNotFound(field='devices')

    @post_dump
    def query_devices(self, data):
        devices_uid = data.get('devices')
        devices_result = Device.query \
            .filter(Device.deviceID.in_(set(devices_uid))) \
            .with_entities(Device.id, Device.deviceID, Device.deviceName) \
            .many()
        devices = []
        for device in devices_result:
            device_record = {
                key: getattr(device, key)
                for key in device.keys()
            }
            devices.append(device_record)
        data['devices'] = devices
        return data


class RuleSchema(BaseSchema):
    ruleName = EmqString(required=True)
    sql = EmqString(required=True, len_max=1000)
    fromTopics = fields.Nested(FromTopicSchema, allow_none=True, many=True)
    scopeData = fields.Nested(ScopeDataSchema)
    ruleType = EmqInteger(required=True, validate=OneOf([1, 2]))
    remark = EmqString(allow_none=True)
    enable = EmqInteger(allow_none=True, validate=OneOf([0, 1]))
    actions = fields.Nested(ActionSchema, only='id', required=True, many=True, dump_only=True)
    userIntID = EmqInteger(dump_only=True)
    tenantID = EmqString(dump_only=True)

    @validates('ruleName')
    def name_is_exist(self, value):
        if self._validate_obj('ruleName', value):
            return

        query = Rule.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Rule.ruleName == value) \
            .first()
        if query:
            raise DataExisted(field='ruleName')

    @validates_schema
    def validate_rule_meta(self, data):
        rule_type = data.get('ruleType')
        # fromTopics is required when ruleType=1
        if rule_type == 1 and not data.get('fromTopics'):
            raise ValidationError(fields.Field.default_error_messages['required'], ['fromTopics'])
        # scopeData is required when ruleType=2
        elif rule_type == 2 and not data.get('scopeData'):
            raise ValidationError(fields.Field.default_error_messages['required'], ['scopeData'])

    @pre_load()
    def remove_from_topics(self, data):
        if data.get('ruleType') == 1:
            data.pop('scopeData', None)
        elif data.get('ruleType') == 2:
            data.pop('fromTopics', None)


class UpdateRuleSchema(RuleSchema):
    ruleName = EmqString(allow_none=True)
    sql = EmqString(allow_none=True, len_max=1000)
    fromTopics = fields.Nested(FromTopicSchema, allow_none=True, many=True)


class AlertActionSchema(BaseSchema):
    alertName = EmqString(required=True)
    alertContent = EmqString(required=True)
    alertSeverity = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))


class EmailActionSchema(BaseSchema):
    title = EmqString(required=True)
    content = EmqString(required=True)
    emails = EmqList(required=True)

    @validates('emails')
    def validate_email(self, value):
        for email in value:
            validate.Email()(email)


class PublishActionSchema(PublishSchema):
    is_private = True
    deviceIntID = EmqInteger(dump_only=True)
    protocol = EmqString()
    prefixTopic = EmqString(len_max=1000)


class MqttActionSchema(BaseSchema):
    topic = EmqString(required=True)


class WebhookActionSchema(BaseSchema):
    url = fields.Url(required=True, len_max=100)
    token = EmqString(required=True, len_min=6)

    @validates_schema
    def validate_webhook(self, data):
        url = data.get('url')
        token = data.get('token')
        if not all([url, token]):
            return
        timestamp = int(time.time())
        nonce = generate_uuid(size=10)
        hash_str = f"{token}{timestamp}{nonce}".encode('utf-8')
        signature = hashlib.sha1(hash_str).hexdigest()

        validate_status = True
        params = dict(signature=signature, timestamp=timestamp, nonce=nonce)
        with SyncHttp() as sync_http:
            response = sync_http.get(url=url, params=params)
        if response.responseCode != 200:
            validate_status = False
        try:
            response_dict = json.loads(response.responseContent)
            if response_dict.get('nonce') != params.get('nonce'):
                validate_status = False
        except Exception:
            validate_status = False
        if not validate_status:
            raise FormInvalid(field='Webhook url')
