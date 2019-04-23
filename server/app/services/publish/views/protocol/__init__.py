from .base import base_publish_json
from .lwm2m import lwm2m_publish_json


PROTOCOL_PUBLISH_JSON_FUNC = {
    1: base_publish_json,  # MQTT
    2: base_publish_json,  # CoAP
    3: lwm2m_publish_json,  # Lwm2m
    6: base_publish_json  # WebSocket
}
