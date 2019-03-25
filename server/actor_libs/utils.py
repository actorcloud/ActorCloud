import os
import glob
import uuid
import subprocess
from typing import AnyStr


def generate_uuid() -> str:
    """
    Generate 32 bit uuid
    """

    uid = str(uuid.uuid1()).replace('-', '')
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uid)).replace('-', '')
    return uid


def get_cwd() -> AnyStr:
    """
    Get the project directory
    """
    try:
        a = os.stat(os.environ['PWD'])
        b = os.stat(os.getcwd())
        if a.st_ino == b.st_ino and a.st_dev == b.st_dev:
            cwd = os.environ['PWD']
        else:
            cwd = os.getcwd()
    except Exception:
        cwd = os.getcwd()
    return cwd


def get_services_path() -> dict:
    """
    Get the services name and path
    :return: dict {service_name:service_path}
    """

    services_dict = {}
    backend_path = get_cwd()
    views_paths_re = os.path.join(backend_path, 'app/*/*/views/')
    views_paths = glob.glob(views_paths_re)
    for views_path in views_paths:
        service_path = os.path.abspath(os.path.join(views_path, os.pardir))
        service_name = os.path.basename(service_path)
        services_dict[service_name] = service_path
    return services_dict


def execute_shell_command(command: AnyStr, output: bool = False, cwd=None) -> AnyStr:
    """ Call subprocess execute command"""

    if not cwd:
        cwd = get_cwd()
    execute_info = ''
    if output:
        try:
            command_list = command.split()
            execute_info = subprocess.check_output(
                command_list, cwd=cwd
            )
        except Exception as e:
            raise RuntimeError(e)
    else:
        try:
            subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output)
    return execute_info


def get_default_device_count() -> AnyStr:
    """
    Get the number of devices that tenant can manage
    """

    from actor_libs.project_config import get_project_config

    project_config = get_project_config()
    default_devices_limit = project_config['DEFAULT_DEVICES_LIMIT']
    return str(default_devices_limit)
