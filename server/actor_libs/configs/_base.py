import glob
import os

import yaml

from actor_libs.utils import get_cwd


__all__ = ['BaseConfig']


class BaseConfig:
    _instance = None
    __base_config = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BaseConfig, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def config(self):
        if not self.__base_config:
            self._load_config()
        return self.__base_config

    def _load_config(self):
        project_path = get_cwd()  # get project path
        self.__base_config['PROJECT_PATH'] = project_path
        default_config_path = os.path.join(project_path, 'config/config.yml')
        instance_config_path = os.path.join(project_path, 'instance/config.yml')
        if os.path.isfile(instance_config_path):
            self._load_yml_config(instance_config_path)
        else:
            self._load_yml_config(default_config_path)
        self._get_certs_path(project_path)
        self._load_emqx_config()
        self._load_actorcloud_config()

    def _load_yml_config(self, file_path):
        with open(file_path, 'r', encoding='utf8') as stream:
            yaml_config = yaml.load(stream).values()
            for dict_config in yaml_config:
                for config_key in dict_config:
                    self.__base_config[config_key.upper()] = dict_config[config_key]

    def _get_certs_path(self, project_path):
        is_exist_certs = glob.glob(os.path.join(project_path, 'instance/certs/actorcloud/*crt'))
        if is_exist_certs:
            certs_path = os.path.join(project_path, 'instance/certs/')
        else:
            certs_path = os.path.join(project_path, 'config/certs/')
        self.__base_config['CERTS_PATH'] = certs_path

    def _load_emqx_config(self):
        api = self.__base_config['EMQX_API']
        lb_ip = self.__base_config['EMQX_LB_IP']
        lb_port = self.__base_config['EMQX_LB_PORT']

        base_url = f"http://{lb_ip}:{lb_port}{api}"
        self.__base_config['EMQX_RULE_URL'] = f"{base_url}/rules"
        self.__base_config['MQTT_PUBLISH_URL'] = f"{base_url}/dmp/publish"
        self.__base_config['LWM2M_PUBLISH_URL'] = f"{base_url}/dmp/publish_lwm2m"

    def _load_actorcloud_config(self):
        backend_node = self.__base_config['BACKEND_NODE']
        api = self.__base_config['ACTORCLOUD_API']

        base_url = f"http://{backend_node}{api}"
        self.__base_config['GATEWAY_CALLBACK_URL'] = f"{base_url}/gateway/publish_callback"
        self.__base_config['MQTT_CALLBACK_URL'] = f"{base_url}/device_publish/mqtt_callback"
        self.__base_config['LWM2M_CALLBACK_URL'] = f"{base_url}/device_publish/lwm2m_callback"
        self.__base_config['LWM2M_SUB_CALLBACK_URL'] = f"{base_url}/lwm2m/subscribe_callback"
