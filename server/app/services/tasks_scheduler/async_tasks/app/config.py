from actor_libs.configs import BaseConfig
from aiohttp import BasicAuth
import os


project_config = BaseConfig().config
emqx_auth = BasicAuth(
    project_config['EMQX_APP_ID'],
    project_config['EMQX_APP_SECRET'])
export_excel_path = os.path.join(
    project_config['PROJECT_PATH'],
    'static/download/export_excels/'
)
download_template_path = os.path.join(
    project_config['PROJECT_PATH'],
    'static/download/templates/'
)
emqx_publish_url = f"{project_config['EMQX_API']}/mqtt/publish"
project_config['EMQX_AUTH'] = emqx_auth
project_config['EMQX_PUBLISH_URL'] = emqx_publish_url
project_config['EXPORT_EXCEL_PATH'] = export_excel_path
project_config['DOWNLOAD_TEMPLATE_PATH'] = download_template_path
