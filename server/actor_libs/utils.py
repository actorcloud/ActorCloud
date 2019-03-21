# coding: utf-8

import os
import glob
from typing import AnyStr


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
    获取模块名称和路径
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
