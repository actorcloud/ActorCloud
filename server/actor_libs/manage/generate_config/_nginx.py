import os
import re
from typing import Set, AnyStr

from flask import current_app

from actor_libs.utils import get_host_ip


__all__ = ['nginx_config']


PROXY_TEMPLATE = """
    location {path} {{
        proxy_pass        http://{upstream}{path};
        proxy_set_header  X-Real-IP  $remote_addr;
    }}
    """
PROXY_STATIC_TEMPLATE = """
    location ^~ {location} {{
        proxy_pass        http://{upstream}{path};
        proxy_set_header  X-Real-IP  $remote_addr;
    }}
"""


def nginx_config():
    project_config = current_app.config
    project_path = project_config['PROJECT_PATH']
    host_ip = get_host_ip()
    host_port = project_config['BACKEND_NODE'].split(':')[-1]
    _generate_services_config(project_path, host_ip, host_port)
    _replace_virtual_host(project_path, host_ip)
    print('Update nginx successfully!')


def _generate_services_config(project_path: AnyStr, host_ip: AnyStr, host_port: AnyStr):
    """ Generate nginx services config of actorcloud """

    routes = _get_flask_url()
    servers_config_path = os.path.join(
        project_path, 'deploy/production/nginx/services/actorcloud.conf'
    )
    with open(servers_config_path, 'w+') as config_file:
        upstream = f'{host_ip}:{host_port}'
        for route in routes:
            if route.endswith('backend_static'):
                template = PROXY_STATIC_TEMPLATE.format(
                    location='/backend_static', path=route, upstream=upstream
                )
            else:
                template = PROXY_TEMPLATE.format(path=route, upstream=upstream)
            config_file.write(template)


def _replace_virtual_host(project_path, host_ip):
    """ replace host_ip in nginx virtual_host.conf """

    virtual_host_path = os.path.join(
        project_path, 'deploy/production/nginx/virtual_host.conf'
    )
    with open(virtual_host_path, 'r') as virtual_host_file:
        ready_config = virtual_host_file.read()
    with open(virtual_host_path, 'w+') as virtual_host_file:
        virtual_host_file.write(ready_config.replace("host-ip", host_ip))


def _get_flask_url() -> Set:
    """ Get all registered routes of current_app """

    rules = list(current_app.url_map.iter_rules())
    routes = set([
        re.sub(r'/<\w+:\w+>.*', '', rule.rule)
        for rule in rules if rule.rule.startswith('/api')
    ])
    return routes
