import os
from typing import Dict

import pytz
from aiohttp import BasicAuth

from actor_libs.project_config import get_project_config


__all__ = ['get_publish_config']


def get_publish_config() -> Dict:
    project_config = get_project_config()
    emq_auth = BasicAuth(
        project_config['EMQX_APP_ID'],
        project_config['EMQX_APP_SECRET'])
    export_excel_path = os.path.join(
        project_config['BACKEND_PATH'],
        'static/download/export_excels/'
    )
    download_template_path = os.path.join(
        project_config['BACKEND_PATH'],
        'static/download/templates/'
    )
    publish_config = {
        'TIMEZONE': pytz.timezone(project_config['TIMEZONE']),
        'POSTGRES_HOST': project_config['POSTGRES_HOST'],
        'POSTGRES_PORT': project_config['POSTGRES_PORT'],
        'POSTGRES_USER': project_config['POSTGRES_USER'],
        'POSTGRES_PASSWORD': project_config['POSTGRES_PASSWORD'],
        'POSTGRES_DATABASE': project_config['POSTGRES_DATABASE'],
        'KAFKA_SERVERS': ';'.join(project_config['KAFKA_SERVERS']),
        'EMQ_AUTH': emq_auth,
        'MQTT_PUBLISH_URL': project_config['MQTT_PUBLISH_URL'],
        'LWM2M_PUBLISH_URL': project_config['LWM2M_PUBLISH_URL'],
        'MQTT_CALLBACK_URL': project_config['MQTT_CALLBACK_URL'],
        'LWM2M_CALLBACK_URL': project_config['LWM2M_CALLBACK_URL'],
        'EXPORT_EXCEL_PATH': export_excel_path,
        'DOWNLOAD_TEMPLATE_PATH': download_template_path,
    }
    return publish_config
