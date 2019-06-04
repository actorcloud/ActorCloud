import glob
import os
from typing import AnyStr, List

import pytz
import yaml
from yaml.loader import FullLoader
from aiohttp import BasicAuth
from requests.auth import HTTPBasicAuth

from actor_libs.utils import get_cwd


__all__ = ['BaseConfig', 'FlaskConfig', 'AsyncTaskConfig', 'TimerTaskConfig']


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
        self._load_yml_config(default_config_path)
        if os.path.isfile(instance_config_path):
            self._load_yml_config(instance_config_path)
        self.__base_config['TIMEZONE'] = pytz.timezone(self.__base_config['TIMEZONE'])
        self._get_certs_path(project_path)
        self._load_emqx_config()
        self._load_actorcloud_config()
        self._load_stream_config()

    def _load_yml_config(self, file_path):
        with open(file_path, 'r', encoding='utf8') as stream:
            yaml_config = yaml.load(stream, Loader=FullLoader).values()
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
        api_version = self.__base_config['EMQX_API_VERSION']
        lb_ip = self.__base_config['EMQX_LB_IP']
        lb_port = self.__base_config['EMQX_LB_PORT']
        self.__base_config['EMQX_API'] = f"http://{lb_ip}:{lb_port}{api_version}"

    def _load_actorcloud_config(self):
        backend_node = self.__base_config['BACKEND_NODE']
        api = self.__base_config['ACTORCLOUD_API']
        base_url = f"http://{backend_node}{api}"
        self.__base_config['CURRENT_ALERT_URL'] = f"{base_url}/current_alerts"

    def _load_stream_config(self):
        stream_ip = self.__base_config['STREAM_IP']
        stream_port = self.__base_config['STREAM_PORT']
        base_url = f"http://{stream_ip}:{stream_port}"
        self.__base_config['STREAM_RULE_URL'] = f"{base_url}/rules"


class FlaskConfig:
    # flask base config
    SESSION_COOKIE_NAME: AnyStr = '_s'
    PERMANENT_SESSION_LIFETIME: int = 3600 * 24 * 30
    TOKEN_LIFETIME: int = 3600 * 24 * 3
    TOKEN_LIFETIME_REMEMBER: int = 3600 * 24 * 30
    TOKEN_LIFETIME_INVITATION: int = 3600 * 24 * 7
    # password bcrypt encryption
    BCRYPT_ROUNDS: int = 10
    BCRYPT_PREFIX: AnyStr = '2a'
    # user config
    RESERVED: List = [
        "user", "topic", "home", "setting", "forgot", "login", "logout",
        "register", "admin", "test", "devices", "product", "group", "public"
    ]
    # upload config
    MAX_CONTENT_LENGTH: int = 104857600  # upload file limit 100mb
    LOGOS_PATH: AnyStr = None
    UPLOADED_EXCELS_DEST: AnyStr = None
    UPLOADED_IMAGES_DEST: AnyStr = None
    UPLOADED_PACKAGES_DEST: AnyStr = None
    EXPORT_EXCEL_PATH: AnyStr = None
    DOWNLOAD_TEMPLATE_EXCEL_DEST: AnyStr = None
    # sqlalchemy config
    SQLALCHEMY_DATABASE_URI: AnyStr = "postgresql://actorcloud:public@server/actorcloud"
    SQLALCHEMY_POOL_SIZE: int = 32
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True
    # emqx config
    EMQX_AUTH: HTTPBasicAuth = None
    # task schedule config
    PUBLISH_TASK_URL: AnyStr = None
    IMPORT_EXCEL_TASK_URL: AnyStr = None
    EXPORT_EXCEL_TASK_URL: AnyStr = None

    @property
    def config(self):
        _cls = self.__class__
        _base_config = BaseConfig().config
        _project_path = _base_config['PROJECT_PATH']
        path_join = os.path.join
        _cls.LOGOS_PATH = path_join(_project_path, 'static/images/')
        _cls.UPLOADED_EXCELS_DEST = path_join(_project_path, 'static/upload/excels/')
        _cls.UPLOADED_IMAGES_DEST = path_join(_project_path, 'static/upload/images/')
        _cls.UPLOADED_PACKAGES_DEST = path_join(_project_path, 'static/upload/packages/')
        _cls.EXPORT_EXCEL_PATH = path_join(_project_path, 'static/download/export_excels')
        _cls.DOWNLOAD_TEMPLATE_EXCEL_DEST = path_join(
            _project_path, 'static/download/templates/'
        )
        _cls.SQLALCHEMY_DATABASE_URI = f"postgresql" \
            f"://{_base_config['POSTGRES_USER']}" \
            f":{_base_config['POSTGRES_PASSWORD']}" \
            f"@{_base_config['POSTGRES_HOST']}" \
            f":{_base_config['POSTGRES_PORT']}" \
            f"/{_base_config['POSTGRES_DATABASE']}"
        _cls.EMQX_AUTH = HTTPBasicAuth(
            username=_base_config['EMQX_APP_ID'],
            password=_base_config['EMQX_APP_SECRET']
        )
        task_schedule_node = f"http://{_base_config['ASYNC_TASKS_NODE']}"
        _cls.IMPORT_EXCEL_TASK_URL = f"{task_schedule_node}/api/v1/import_excels"
        _cls.EXPORT_EXCEL_TASK_URL = f"{task_schedule_node}/api/v1/export_excels"

        for key, value in _cls.__dict__.items():
            if key.isupper():
                _base_config[key] = value
        return _base_config


class AsyncTaskConfig:
    EMQX_AUTH: BasicAuth = None
    EMQX_PUBLISH_URL: AnyStr = None
    EXPORT_EXCEL_PATH: AnyStr = None
    DOWNLOAD_TEMPLATE_PATH: AnyStr = None

    @property
    def config(self):
        _cls = self.__class__
        _base_config = BaseConfig().config
        _project_path = _base_config['PROJECT_PATH']
        path_join = os.path.join
        _cls.EMQX_AUTH = BasicAuth(
            _base_config['EMQX_APP_ID'],
            _base_config['EMQX_APP_SECRET']
        )
        _cls.EMQX_PUBLISH_URL = f"{_base_config['EMQX_API']}/mqtt/publish"
        _cls.EMQX_PUBLISH_URL = f"{_base_config['EMQX_API']}/mqtt/publish"
        _cls.EXPORT_EXCEL_PATH = path_join(_project_path, 'static/download/export_excels/')
        _cls.DOWNLOAD_TEMPLATE_PATH = path_join(_project_path, 'static/download/templates/')

        for key, value in _cls.__dict__.items():
            if key.isupper():
                _base_config[key] = value
        return _base_config


class TimerTaskConfig:
    PUBLISH_TASK_URL: AnyStr = None

    @property
    def config(self):
        _cls = self.__class__
        _base_config = BaseConfig().config
        task_schedule_node = f"http://{_base_config['ASYNC_TASKS_NODE']}"
        _cls.PUBLISH_TASK_URL = f"{task_schedule_node}/api/v1/device_publish"

        for key, value in _cls.__dict__.items():
            if key.isupper():
                _base_config[key] = value
        return _base_config
