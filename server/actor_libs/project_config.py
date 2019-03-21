# coding: utf-8

import glob
import os
from typing import AnyStr, Dict

import yaml


__all__ = ['get_project_config']


def get_project_config():
    """ 生成项目配置文件 """

    project_config = {}

    # 获取actorcloud 所在目录
    backend_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )
    project_config['BACKEND_PATH'] = backend_path

    # 加载 config/config.yml 里的配置
    default_config_file = os.path.join(backend_path, 'config/config.yml')
    default_config = _config_from_yaml(default_config_file)
    project_config.update(default_config)

    # 加载 instance/config.yml 里的配置
    instance_config_file = os.path.join(backend_path, 'instance/config.yml')
    if os.path.isfile(instance_config_file):
        instance_config = _config_from_yaml(instance_config_file)
        project_config.update(instance_config)
    # 更新证书位置(emqx, pay)
    project_config['CERTS_PATH'] = _get_certs_path(backend_path)
    # 更新emqx配置
    project_config.update(_get_emq_config(project_config))
    return project_config


def _get_certs_path(backend_path: AnyStr):
    """ 生成证书路径 """

    is_exist_certs = glob.glob(os.path.join(backend_path, 'instance/certs/*crt'))
    if is_exist_certs:
        certs_path = os.path.join(backend_path, 'instance/certs/')
    else:
        certs_path = os.path.join(backend_path, 'config/certs/')
    return certs_path


def _get_emq_config(project_config: Dict) -> Dict:
    """ 公共 emqx 下发配置 """

    mqtt_publish_url = f"http://{project_config['EMQX_LB_IP']}" \
                       f":{project_config['EMQX_API_PORT']}/api/v2/dmp/publish"
    lwm2m_publish_url = f"http://{project_config['EMQX_LB_IP']}" \
                        f":{project_config['EMQX_API_PORT']}/api/v2/dmp/publish_lwm2m"
    mqtt_callback_url = f"http://{project_config['BACKEND_NODE']}" \
                        f"/api/v1/device_publish/mqtt_callback"
    lwm2m_callback_url = f"http://{project_config['BACKEND_NODE']}" \
                         f"/api/v1/device_publish/lwm2m_callback"
    gateway_callback_url = f"http://{project_config['BACKEND_NODE']}" \
                           f"/api/v1/gateway/publish_callback"
    emq_config = {
        'MQTT_PUBLISH_URL': mqtt_publish_url,
        'LWM2M_PUBLISH_URL': lwm2m_publish_url,
        'MQTT_CALLBACK_URL': mqtt_callback_url,
        'LWM2M_CALLBACK_URL': lwm2m_callback_url,
        'GATEWAY_CALLBACK_URL': gateway_callback_url
    }
    return emq_config


def _config_from_yaml(file_path):
    """ 读取yml文件 """

    config_dict = {}
    with open(file_path, 'r', encoding='utf8') as stream:
        yaml_config = yaml.load(stream).values()
        for dict_config in yaml_config:
            for config_key in dict_config:
                config_dict[config_key.upper()] = dict_config[config_key]
    return config_dict
