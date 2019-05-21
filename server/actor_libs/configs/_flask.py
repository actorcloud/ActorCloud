import os

from requests.auth import HTTPBasicAuth

from ._base import BaseConfig


__all__ = ['FlaskConfig']


class FlaskConfig:
    __config = BaseConfig().config

    def __init__(self):
        self.__dict__ = self.__config

    @property
    def config(self):
        return self.__dict__


# base flask config
_config = FlaskConfig()
_config.SESSION_COOKIE_NAME = '_s'
_config.PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30
_config.TOKEN_LIFETIME = 3600 * 24 * 3
_config.TOKEN_LIFETIME_REMEMBER = 3600 * 24 * 30
_config.TOKEN_LIFETIME_INVITATION = 3600 * 24 * 7
# password bcrypt encryption
_config.BCRYPT_ROUNDS = 10
_config.BCRYPT_PREFIX = '2a'
# user config
_config.RESERVED = [
    "user", "topic", "home", "setting", "forgot", "login", "logout",
    "register", "admin", "test", "devices", "product", "group", "public"
]
# upload config
_config.MAX_CONTENT_LENGTH = 104857600  # upload file limit 100mb
_config.LOGOS_PATH = os.path.join(_config.PROJECT_PATH, 'static/images/')
_config.UPLOADED_EXCELS_DEST = os.path.join(_config.PROJECT_PATH, 'static/upload/excels/')
_config.UPLOADED_IMAGES_DEST = os.path.join(_config.PROJECT_PATH, 'static/upload/images/')
_config.UPLOADED_PACKAGES_DEST = os.path.join(_config.PROJECT_PATH, 'static/upload/packages/')
_config.EXPORT_EXCEL_PATH = os.path.join(_config.PROJECT_PATH, 'static/download/export_excels')
_config.DOWNLOAD_TEMPLATE_EXCEL_DEST = os.path.join(
    _config.PROJECT_PATH, 'static/download/templates/'
)
# sqlalchemy config
_config.SQLALCHEMY_DATABASE_URI = f"postgresql" \
    f"://{_config.POSTGRES_USER}" \
    f":{_config.POSTGRES_PASSWORD}" \
    f"@{_config.POSTGRES_HOST}" \
    f":{_config.POSTGRES_PORT}" \
    f"/{_config.POSTGRES_DATABASE}"  # postgresql://username:password@server/db
_config.SQLALCHEMY_POOL_SIZE = 32
_config.SQLALCHEMY_TRACK_MODIFICATIONS = True
# emqx config
_config.EMQX_AUTH = HTTPBasicAuth(
    username=_config.EMQX_APP_ID,
    password=_config.EMQX_APP_SECRET
)
# task schedule config
_config.PUBLISH_TASK_URL = f"http://{_config.TASK_SCHEDULER_NODE}/api/v1/publish_tasks"
_config.IMPORT_EXCEL_TASK_URL = f"http://{_config.TASK_SCHEDULER_NODE}/api/v1/import_excels"
_config.EXPORT_EXCEL_TASK_URL = f"http://{_config.TASK_SCHEDULER_NODE}/api/v1/export_excels"
