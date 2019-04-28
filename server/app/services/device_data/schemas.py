from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDateTime, EmqString
)


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
