from flask import g
from marshmallow import (
    validates, pre_load, fields, validates_schema, post_dump
)
from marshmallow.validate import OneOf

from actor_libs.database.orm import db
from actor_libs.errors import DataExisted, DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger, EmqDict
)
from app.models import (
    Product, BusinessRule, Device, Action, DataStream
)


__all__ = [
    'BusinessRuleSchema', 'ActionSchema', 'AlertActionSchema', 'UpdateBusinessRuleSchema'
]


class ActionSchema(BaseSchema):
    actionName = EmqString(required=True)
    actionType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
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
            ...
        elif action_type == 3:
            ...
        elif action_type == 4:
            ...
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


class BusinessRuleSchema(BaseSchema):
    ruleName = EmqString(required=True)
    sql = EmqString(required=True, len_max=1000)
    fromTopics = fields.Nested(FromTopicSchema, required=True, many=True)
    remark = EmqString(allow_none=True)
    enable = EmqInteger(allow_none=True)
    actions = fields.Nested(ActionSchema, only='id', required=True, many=True, dump_only=True)
    userIntID = EmqInteger(dump_only=True)
    tenantID = EmqString(dump_only=True)

    @validates('ruleName')
    def name_is_exist(self, value):
        if self._validate_obj('ruleName', value):
            return

        query = BusinessRule.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(BusinessRule.ruleName == value) \
            .first()
        if query:
            raise DataExisted(field='ruleName')


class UpdateBusinessRuleSchema(BusinessRuleSchema):
    ruleName = EmqString(allow_none=True)
    sql = EmqString(allow_none=True, len_max=1000)
    fromTopics = fields.Nested(FromTopicSchema, allow_none=True, many=True)


class AlertActionSchema(BaseSchema):
    alertName = EmqString(required=True)
    alertContent = EmqString(required=True)
    alertSeverity = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
