from typing import Dict

import pytz

from actor_libs.project_config import get_project_config


__all__ = ['get_aggr_config']


def get_aggr_config() -> Dict:
    project_config = get_project_config()
    timezone = pytz.timezone(project_config['TIMEZONE'])
    aggr_config = {
        'TIMEZONE': timezone,
        'POSTGRES_HOST': project_config['POSTGRES_HOST'],
        'POSTGRES_PORT': project_config['POSTGRES_PORT'],
        'POSTGRES_USER': project_config['POSTGRES_USER'],
        'POSTGRES_PASSWORD': project_config['POSTGRES_PASSWORD'],
        'POSTGRES_DATABASE': project_config['POSTGRES_DATABASE'],
        'KAFKA_SERVERS': ';'.join(project_config['KAFKA_SERVERS']),
        'DEFAULT_DEVICES_LIMIT': project_config['DEFAULT_DEVICES_LIMIT']
    }
    return aggr_config
