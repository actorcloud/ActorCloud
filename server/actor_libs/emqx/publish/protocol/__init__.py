from .base import base_publish_json
from .lwm2m import lwm2m_publish_json


PROTOCOL_PUBLISH_JSON_FUNC = {
    'mqtt': base_publish_json,
    'coap': base_publish_json,
    'lwm2m': lwm2m_publish_json,
    'websocket': base_publish_json
}
