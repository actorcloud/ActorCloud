from ._nginx import nginx_config
from ._supervisor import supervisor_config


__all__ = ['generate_deploy_config']


def generate_deploy_config():
    nginx_config()
    supervisor_config()
