import ujson
import arrow
from arrow.parser import ParserError
from flask import g, current_app
from marshmallow import pre_load, post_load, post_dump
from marshmallow.validate import OneOf
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound, FormInvalid
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import EmqString, EmqInteger, EmqDateTime, EmqDict
from actor_libs.utils import check_interval_time
from app.models import Client, Product, DictCode


__all__ = [
    'ClientPublishSchema', 'ClientPublishLogSchema', 'TimerPublishSchema',
]


class ClientPublishSchema(BaseSchema):
    """
    Device publish schema
    controlType: 1 -> publish(mqtt)，2 -> read，3 -> write，4 -> execute
    prefixTopic: /protocol/tenantID/productID/deviceID/
    """

    deviceID = EmqString(required=True)
    topic = EmqString(required=True, len_max=1000)
    payload = EmqString(required=True, len_max=10000)
    streamID = EmqInteger(allow_none=True)
    controlType = EmqInteger(allow_none=True, validate=OneOf([1, 2, 3, 4]))
    clientIntID = EmqInteger(load_only=True)  # client index id
    cloudProtocol = EmqInteger(load_only=True)  # product cloud protocol: 1,2,3,4...
    prefixTopic = EmqString(load_only=True, len_max=1000)

    @pre_load
    def handle_data(self, data):
        device_uid = data.get('deviceID')
        if not isinstance(device_uid, str):
            raise FormInvalid(field='deviceID')
        client_info = db.session \
            .query(Client.id, Client.productID, Client.tenantID,
                   DictCode.codeValue.label('cloudProtocol'),
                   func.lower(DictCode.enLabel).label('protocol')) \
            .join(Product, Product.productID == Client.productID) \
            .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
            .filter(Client.deviceID == device_uid, Client.tenantID == g.tenant_uid,
                    DictCode.code == 'cloudProtocol').to_dict()
        data.update(client_info)
        data['prefixTopic'] = (
            f"{data['protocol']}/{data['tenantID']}/"
            f"{data['productID']}/{data['deviceID']}/"
        )
        data['topic'] = data['topic'] if data.get('topic') else 'inbox'
        return data

    @post_load
    def handle_protocol_publish(self, data):
        protocol_func = HANDLE_PROTOCOL_FUNC.get(data['cloudProtocol'])
        if not protocol_func:
            raise DataNotFound(field='cloudProtocol')
        data = protocol_func(data)
        return data


class ClientPublishLogSchema(ClientPublishSchema):
    payload = EmqDict()
    publishStatus = EmqInteger(dump_only=True)

    @post_dump
    def dump_payload(self, data):
        """ payload type dict to json"""
        payload = data.get('payload')
        if payload:
            data['payload'] = ujson.dumps(payload)
        return data


class TimerPublishSchema(BaseSchema):
    taskName = EmqString(required=True)
    taskStatus = EmqInteger(dump_only=True)
    timerType = EmqInteger(required=True, validate=OneOf([1, 2]))
    deviceID = EmqString(required=True)
    controlType = EmqInteger(required=True, validate=OneOf([1, 2, 3, 4]))
    topic = EmqString(allow_none=True, len_max=500)
    path = EmqString(allow_none=True, len_max=500)
    payload = EmqString(required=True, len_max=10000)
    intervalTime = EmqDict(allow_none=True)
    crontabTime = EmqDateTime(allow_none=True)

    @post_load
    def handle_data(self, data):
        data['taskStatus'] = 2
        data = self.validate_timer_format(data)
        data = self.handle_publish_object(data)
        return data

    @staticmethod
    def handle_publish_object(data):

        publish_type = data['publishType']
        device_uid = data.get('deviceID')
        group_uid = data.get('groupID')
        if publish_type == 1 and device_uid and not group_uid:
            result = DevicePublishSchema().load({**data}).data
            data['deviceIntID'] = result['deviceIntID']
            data['payload'] = result['payload']
            data['topic'] = result['topic'] if result.get('topic') else None
            data['path'] = result['path'] if result.get('path') else None
            data['protocol'] = result['protocol']
            raise FormInvalid(field='publishType')
        data['payload'] = ujson.loads(data['payload'])
        return data

    @staticmethod
    def validate_timer_format(data):

        timer_type = data.get('timerType')
        interval_time = data.get('intervalTime')
        crontab_time = data.get('crontabTime')

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
        return data


def _base_protocol(data):
    """ handle base protocol: mqtt, websocket, modbus, http """

    if not data.get('controlType'):
        data['controlType'] = 1
    return data


def _lwm2m_protocol(data):
    """ handle lwm2m protocol publish """

    path = data['topic']
    # todo
    return data


HANDLE_PROTOCOL_FUNC = {
    1: _base_protocol,  # MQTT
    2: _base_protocol,  # CoAP
    3: _lwm2m_protocol,  # LwM2M
    6: _base_protocol  # cloudProtocol
}
