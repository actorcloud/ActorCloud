import os
from multiprocessing import cpu_count
from typing import AnyStr

from flask import current_app

from .jinja_templates import insert_jinja_template


__all__ = ['gunicorn_config']


def gunicorn_config() -> AnyStr:
    """ Generate configuration information of gunicorn """

    project_config = current_app.config
    project_path = project_config['PROJECT_PATH']
    gunicorn_config_path = os.path.join(
        project_path, 'deploy/production/gunicorn/config.py'
    )
    get_cpu_count = cpu_count()
    if get_cpu_count > 8:
        worker_cpu = 9
    elif get_cpu_count <= 2:
        worker_cpu = 3
    else:
        worker_cpu = get_cpu_count * 2 + 1

    backend_node = project_config['BACKEND_NODE']
    port = backend_node.split(':')[-1]
    jinja_config = {
        'host': f"0.0.0.0:{port}",
        'worker': worker_cpu,
        'loglevel': project_config['LOG_LEVEL']
    }
    insert_jinja_template(
        project_path=project_path,
        out_path=gunicorn_config_path,
        template_name='gunicorn.jinja',
        jinja_config=jinja_config
    )
    return gunicorn_config_path
