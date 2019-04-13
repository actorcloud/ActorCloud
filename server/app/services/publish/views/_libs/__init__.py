from .device import (
    lwm2m_device_publish, mqtt_device_publish, lora_device_publish
)
from .group import group_publish_task_scheduler


DEVICE_PUBLISH_FUNC = {
    'mqtt': mqtt_device_publish,
    'lwm2m': lwm2m_device_publish,
    'lora': lora_device_publish
}
