import json

import arrow
from arrow.parser import ParserError
from flask import current_app
from marshmallow import post_load, post_dump
from marshmallow.validate import OneOf

from actor_libs.emqx.publish.schemas import PublishSchema
from actor_libs.errors import FormInvalid
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger, EmqDateTime, EmqDict
)
from actor_libs.utils import check_interval_time


__all__ = [
    'PublishLogSchema', 'TimerPublishSchema',
]


class PublishLogSchema(PublishSchema):
    msgTime = EmqDateTime(dump_only=True)
    payload = EmqDict()
    publishStatus = EmqInteger(dump_only=True)

    @post_dump
    def dump_payload(self, data):
        """ payload type dict to json"""

        payload = data.get('payload')
        if payload:
            data['payload'] = json.dumps(payload)
        return data


class TimerPublishSchema(BaseSchema):
    taskName = EmqString(required=True)
    deviceID = EmqString(required=True)
    topic = EmqString(required=True, len_max=500)  # publish topic
    payload = EmqString(required=True, len_max=10000)  # publish payload
    timerType = EmqInteger(required=True, validate=OneOf([1, 2]))
    intervalTime = EmqDict(allow_none=True)
    crontabTime = EmqDateTime(allow_none=True)
    deviceIntID = EmqInteger(allow_none=True)  # client index id
    taskStatus = EmqInteger(dump_only=True)

    @post_load
    def handle_data(self, data):
        data['taskStatus'] = 2
        data = self.validate_timer_format(data)
        result = PublishSchema().load({**data}).data
        data['deviceIntID'] = result['deviceIntID']
        data['payload'] = result['payload']
        data['topic'] = result['topic'] if result.get('topic') else None
        data['payload'] = json.loads(data['payload'])
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
