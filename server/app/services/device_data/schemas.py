from typing import AnyStr

import ujson
from flask import g, request
from marshmallow.validate import OneOf
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDateTime, EmqDict, EmqInteger, EmqList, EmqString
)
from actor_libs.utils import generate_uuid


__all__ = ['DeviceEventSchema', 'ClientConnectLogSchema']


class DeviceEventSchema(BaseSchema):
    msgTime = EmqDateTime(allow_none=True)
    topic = EmqString(required=True)
    payload_string = EmqString(required=True)


class ClientConnectLogSchema(BaseSchema):
    class Meta:
        additional = (
            'deviceID', 'connectStatus', 'IP', 'keepAlive', 'msgTime'
        )
