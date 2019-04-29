from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import EmqDateTime, EmqString, EmqInteger


__all__ = ['DeviceEventSchema', 'ConnectLogSchema']


class DeviceEventSchema(BaseSchema):
    msgTime = EmqDateTime(allow_none=True)
    streamID = EmqString(required=True)
    topic = EmqString(required=True)
    dataType = EmqInteger(required=True)
    data = EmqString(required=True)
    responseResult = EmqString(required=True)


class ConnectLogSchema(BaseSchema):
    class Meta:
        additional = (
            'deviceID', 'connectStatus', 'IP', 'keepAlive', 'msgTime'
        )
