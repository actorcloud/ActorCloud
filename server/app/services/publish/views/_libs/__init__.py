from .client import (
    lwm2m_client_publish, mqtt_client_publish, lora_client_publish
)


DEVICE_PUBLISH_FUNC = {
    'mqtt': mqtt_client_publish,
    'lwm2m': lwm2m_client_publish,
    'lora': lora_client_publish
}
