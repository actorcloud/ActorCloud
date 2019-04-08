from typing import Dict

import arrow
from arrow.parser import ParserError
from flask import g, current_app
from marshmallow import pre_load, post_load, validates, post_dump, validates_schema
from marshmallow.validate import OneOf
from sqlalchemy import func
import ujson

from actor_libs.database.orm import db
from actor_libs.emqx.publish.lwm2m_publish import (
    get_lwm2m_item_by_path, check_control_type
)
from actor_libs.errors import DataNotFound, FormInvalid
from actor_libs.utils import check_interval_time
from app.models import (
    Client, Product, Group, GroupDevices, User, DictCode
)
from .base import BaseSchema, EmqString, EmqInteger, EmqDateTime, EmqDict


__all__ = [
    'DevicePublishSchema', 'GroupPublishSchema', 'TimerPublishSchema',
]


class DevicePublishSchema(BaseSchema):
    """
    Device publish schema
    controlType: 1 -> publish(mqtt)，2 -> read，3 -> write，4 -> execute
    """

    payload = EmqString(allow_none=True, len_max=10000)
    topic = EmqString(allow_none=True, len_max=500)
    path = EmqString(allow_none=True, len_max=500)
    controlType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
    deviceID = EmqString(required=True)
    productID = EmqString(load_only=True)
    protocol = EmqString(load_only=True)
    cloudProtocol = EmqInteger(allow_none=True)
    deviceIntID = EmqInteger(load_only=True)
    userIntID = EmqInteger(load_only=True)
    tenantID = EmqString(load_only=True)
    publishType = EmqInteger(load_only=True)
    streamID = EmqInteger(load_only=True)

    @validates_schema
    def validate_payload(self, in_data):
        protocol = in_data['protocol']
        payload = in_data.get('payload')
        if protocol != 'lwm2m':
            try:
                ujson.loads(payload)
            except Exception:
                raise FormInvalid(field='payload')

    @pre_load
    def handle_in_data(self, in_data):

        device_uid = in_data.get('deviceID')
        if not isinstance(device_uid, str):
            raise FormInvalid(field='deviceID')
        query = db.session \
            .query(Client.id, Product.productID,
                   DictCode.codeValue, func.lower(DictCode.codeLabel)) \
            .join(Product, Product.productID == Client.productID) \
            .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
            .filter(Client.deviceID == device_uid, Client.tenantID == g.tenant_uid,
                    DictCode.code == 'cloudProtocol') \
            .first()
        if not query:
            raise DataNotFound(field='deviceID')
        device_id, product_uid, cloud_protocol, protocol = query
        in_data['productID'] = product_uid
        in_data['cloudProtocol'] = cloud_protocol
        in_data['protocol'] = protocol
        in_data['deviceIntID'] = device_id
        in_data['tenantID'] = g.tenant_uid
        in_data['userIntID'] = g.user_id
        in_data['publishType'] = 1

        if protocol == 'lwm2m':
            in_data = self.handle_lwm2m(in_data)
        else:
            in_data = self.handle_mqtt(in_data)
        in_data = self.wrap_payload(in_data)
        return in_data

    @staticmethod
    def handle_mqtt(in_data) -> Dict:

        control_type = in_data.get('controlType')
        if control_type != 1:
            raise FormInvalid(field='controlType')
        in_data['controlType'] = 1
        if not in_data.get('topic'):
            in_data['topic'] = 'inbox'
        return in_data

    @staticmethod
    def handle_lwm2m(in_data) -> Dict:

        if not in_data.get('path'):
            raise FormInvalid(field='path')
        control_type = in_data.get('controlType')
        # controlType must be on of 2,3,4
        if control_type not in [2, 3, 4]:
            raise FormInvalid(field='controlType')
        if in_data['path'] == '/19/1/0':
            return in_data

        item_dict = get_lwm2m_item_by_path(
            in_data['path'], in_data['deviceIntID'], in_data['tenantID']
        )
        check_status = check_control_type(
            control_type, item_dict['item_operations']
        )
        if not check_status:
            raise FormInvalid(field='controlType')
        if control_type == 2:
            in_data['payload'] = ''
        elif control_type == 3 and in_data.get('payload') is None:
            raise FormInvalid(field='payload')
        elif control_type == 4 and in_data.get('payload') is None:
            in_data['payload'] = ''
        return in_data

    @staticmethod
    def wrap_payload(in_data):

        path = in_data.get('path')
        cloud_protocol = in_data.get('cloudProtocol')
        # TODO Support other protocol
        if cloud_protocol == 3 and path == '/19/1/0' or cloud_protocol == 1:
            if in_data.get('payload') is None:
                raise FormInvalid(field='payload')
            try:
                data = ujson.loads(in_data.get('payload'))
            except Exception:
                raise FormInvalid(field='payload')
            payload = {'data': data, 'data_type': 'request'}
            if in_data.get('streamID'):
                payload['stream_id'] = in_data['streamID']
            in_data['payload'] = ujson.dumps(payload)
        return in_data


class GroupPublishSchema(BaseSchema):
    topic = EmqString(allow_none=True, len_max=500)
    path = EmqString(allow_none=True, len_max=500)
    payload = EmqString(required=True, len_max=10000)
    controlType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
    groupID = EmqString(required=True)
    productID = EmqString(load_only=True)
    protocol = EmqString(load_only=True)
    cloudProtocol = EmqInteger(allow_none=True)
    groupIntID = EmqInteger(load_only=True)
    publishType = EmqInteger(load_only=True)
    userIntID = EmqInteger(load_only=True)
    tenantID = EmqString(load_only=True)

    @validates('payload')
    def validate_payload(self, value):
        try:
            ujson.loads(value)
        except Exception:
            raise FormInvalid(field='payload')

    @pre_load
    def handle_in_data(self, in_data):

        group_uid = in_data.get('groupID')
        if not isinstance(group_uid, str):
            raise FormInvalid(field='groupID')
        query = db.session \
            .query(Group.id, Product.productID,
                   DictCode.codeValue, func.lower(DictCode.codeLabel)) \
            .join(Product, Product.productID == Group.productID) \
            .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
            .join(User, User.id == Group.userIntID) \
            .filter(Group.groupID == group_uid, User.tenantID == g.tenant_uid,
                    DictCode.code == 'cloudProtocol') \
            .first()
        if not query:
            raise DataNotFound(field='groupID')
        group_devices = db.session \
            .query(func.count(GroupDevices.c.deviceIntID)) \
            .filter(GroupDevices.c.groupID == group_uid).scalar()
        if not group_devices:
            raise DataNotFound(field='groupDevices')
        group_id, product_uid, cloud_protocol, protocol = query
        in_data['productID'] = product_uid
        in_data['cloudProtocol'] = cloud_protocol
        in_data['protocol'] = protocol
        in_data['groupIntID'] = group_id
        in_data['tenantID'] = g.tenant_uid
        in_data['userIntID'] = g.user_id
        in_data['publishType'] = 2

        if protocol == 'lwm2m':
            raise DataNotFound(field='Nonsupport_Lwm2m')
        else:
            self.handle_mqtt(in_data)
        return in_data

    @staticmethod
    def handle_mqtt(in_data) -> Dict:
        control_type = in_data.get('controlType')
        if control_type != 1:
            raise FormInvalid(field='controlType')
        in_data['controlType'] = 1
        if not in_data.get('topic'):
            in_data['topic'] = 'inbox'
        return in_data

    @staticmethod
    def handle_lwm2m(in_data) -> Dict:
        return in_data


class TimerPublishSchema(BaseSchema):
    taskName = EmqString(required=True)
    taskStatus = EmqInteger(dump_only=True)
    timerType = EmqInteger(required=True, validate=OneOf([1, 2]))
    publishType = EmqInteger(required=True, validate=OneOf([1, 2]))  # 1:device, 2:group
    controlType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
    topic = EmqString(allow_none=True, len_max=500)
    path = EmqString(allow_none=True, len_max=500)
    payload = EmqString(required=True, len_max=10000)
    intervalTime = EmqDict(allow_none=True)
    crontabTime = EmqDateTime(allow_none=True)
    groupID = EmqString(allow_none=True)
    deviceID = EmqString(allow_none=True)
    userIntID = EmqInteger(dump_only=True)
    deviceIntID = EmqString(dump_only=True)
    protocol = EmqString(load_only=True)
    streamID = EmqInteger(load_only=True)

    @post_dump
    def handle_dump_data(self, in_data):
        if in_data['publishType'] == 1:
            del in_data['groupID']
        else:
            del in_data['deviceIntID']
        return in_data

    @post_load
    def handle_in_data(self, in_data):
        in_data['userIntID'] = g.user_id
        in_data['taskStatus'] = 2
        in_data = self.validate_timer_format(in_data)
        in_data = self.handle_publish_object(in_data)
        return in_data

    @staticmethod
    def handle_publish_object(in_data):

        publish_type = in_data['publishType']
        device_uid = in_data.get('deviceID')
        group_uid = in_data.get('groupID')
        if publish_type == 1 and device_uid and not group_uid:
            result = DevicePublishSchema().load({**in_data}).data
            in_data['deviceIntID'] = result['deviceIntID']
            in_data['payload'] = result['payload']
            in_data['topic'] = result['topic'] if result.get('topic') else None
            in_data['path'] = result['path'] if result.get('path') else None
            in_data['protocol'] = result['protocol']
        elif publish_type == 2 and group_uid and not device_uid:
            result = GroupPublishSchema().load({**in_data}).data
            in_data['payload'] = result['payload']
            in_data['protocol'] = result['protocol']
        else:
            raise FormInvalid(field='publishType')
        in_data['payload'] = ujson.loads(in_data['payload'])
        return in_data

    @staticmethod
    def validate_timer_format(in_data):

        timer_type = in_data.get('timerType')
        interval_time = in_data.get('intervalTime')
        crontab_time = in_data.get('crontabTime')

        if timer_type == 1 and crontab_time and not interval_time:
            date_now = arrow.now(tz=current_app.config['TIMEZONE']).shift(minutes=+2)
            try:
                crontab_time = arrow.get(crontab_time)
            except ParserError:
                raise FormInvalid(field='crontabTime')
            if crontab_time < date_now:
                FormInvalid(field='crontabTime')
        elif timer_type == 2 and interval_time and not crontab_time:
            check_status = check_interval_time(interval_time)
            if not check_status:
                raise FormInvalid(field='intervalTime')
        else:
            raise FormInvalid(field='timerType')
        return in_data
