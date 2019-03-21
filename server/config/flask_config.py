# coding: utf-8

from actor_libs.project_config import get_project_config


__all__ = ['get_flask_config']


def get_flask_config():
    """ get flask all config """

    project_config = get_project_config()

    flask_config = _base_backend_config(project_config)
    flask_config.update(_db_config(project_config))
    flask_config.update(_emqx_config(project_config))
    flask_config.update(_task_config(project_config))
    flask_config.update(_file_path_config(project_config))
    flask_config.update(_email_config(project_config))
    return flask_config


def _base_backend_config(project_config):
    """ actorcloud backend base config """

    from actor_libs.utils import get_services_path

    base_config = {
        'TIMEZONE': project_config['TIMEZONE'],  # timezone
        'RESERVED': [
            "user", "topic", "home", "setting", "forgot", "login", "logout",
            "register", "admin", "test", "devices", "product", "group", "public"
        ],  # reserved user list
        'BCRYPT_ROUNDS': 10,  # bcrypt db encryption
        'BCRYPT_PREFIX': '2a',  # bcrypt db encryption
        'SECRET_KEY': project_config['SECRET_KEY'],  # flask token secret key
        'SESSION_COOKIE_NAME': '_s',  # flask cookie name
        'PERMANENT_SESSION_LIFETIME': 3600 * 24 * 30,  # session lifetime
        'TOKEN_LIFETIME': 3600 * 24 * 3,  # token
        'TOKEN_LIFETIME_REMEMBER': 3600 * 24 * 30,
        'TOKEN_LIFETIME_INVITATION': 3600 * 24 * 7,
        'CERTS_PATH': project_config['CERTS_PATH'],  # emqx or pay certs
        'ADMIN_EMAIL': project_config['ADMIN_EMAIL'],  # admin user
        'ADMIN_PASSWORD': project_config['ADMIN_PASSWORD'],  # admin password
        'DEFAULT_DEVICES_LIMIT': project_config['DEFAULT_DEVICES_LIMIT']
    }

    # check product mall display
    if get_services_path().get('product_mall'):
        base_config['showProductsMall'] = 1
    else:
        base_config['showProductsMall'] = 0
        base_config['DEFAULT_DEVICES_LIMIT'] = -1  # not limit
    return base_config


def _file_path_config(project_config):
    """ backend file path config"""

    from os.path import join

    backend_path = project_config['BACKEND_PATH']
    path_config = {
        'BACKEND_PATH': backend_path,
        'MAX_CONTENT_LENGTH': 104857600,  # 100mb
        'UPLOADED_EXCELS_DEST': join(backend_path, 'static/upload/excels/'),
        'UPLOADED_IMAGES_DEST': join(backend_path, 'static/upload/images/'),
        'UPLOADED_PACKAGES_DEST': join(backend_path, 'static/upload/packages/'),
        'DOWNLOAD_TEMPLATE_EXCEL_DEST': join(backend_path, 'static/download/templates/'),
        'LOGOS_PATH': join(backend_path, 'static/images/'),  # log file
        'EXPORT_EXCEL_PATH': join(backend_path, 'static/download/export_excels/')
    }
    return path_config


def _db_config(project_config):
    """ postgres, redis """

    # postgres db url: postgresql://username:password@server/db
    sqlalchemy_db_url = f"postgresql://{project_config['POSTGRES_USER']}" \
                        f":{project_config['POSTGRES_PASSWORD']}" \
                        f"@{project_config['POSTGRES_HOST']}" \
                        f":{project_config['POSTGRES_PORT']}" \
                        f"/{project_config['POSTGRES_DATABASE']}"
    sqlalchemy_pool_size = 20

    db_config = {
        'SQLALCHEMY_DATABASE_URI': sqlalchemy_db_url,
        'SQLALCHEMY_POOL_SIZE': sqlalchemy_pool_size,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True
    }
    return db_config


def _email_config(project_config):
    """ email config: invitation register """

    email_config = {
        'SITE_NAME': project_config['SITE_NAME'],  # send email site name
        'SITE_DOMAIN': project_config['SITE_DOMAIN'],  # send email site domain
        'EMAIL_TITLE': project_config['EMAIL_TITLE'],  # send email title
        'MAIL_SERVER': project_config['MAIL_SERVER'],
        'MAIL_PORT': project_config['MAIL_PORT'],
        'MAIL_USE_SSL': project_config['MAIL_USE_SSL'],
        'MAIL_USERNAME': project_config['MAIL_USERNAME'],
        'MAIL_PASSWORD': project_config['MAIL_PASSWORD'],
        'MAIL_DEFAULT_SENDER': project_config['MAIL_DEFAULT_SENDER'],
    }
    return email_config


def _emqx_config(project_config):
    """ emqx config: rule publish"""

    from requests.auth import HTTPBasicAuth

    emqx_auth = HTTPBasicAuth(
        username=project_config['EMQX_APP_ID'],
        password=project_config['EMQX_APP_SECRET']
    )
    emqx_rule_url = f"http://{project_config['EMQX_LB_IP']}" \
                    f":{project_config['EMQX_API_PORT']}/api/v2/rules"
    lwm2m_sub_callback_url = f"http://{project_config['BACKEND_NODE']}" \
                             f"/api/v1/lwm2m/subscribe_callback"
    emqx_config = {
        'EMQX_AUTH': emqx_auth,
        'EMQX_RULE_URL': emqx_rule_url,
        'EMQX_NODES': project_config['EMQX_NODES'],
        'MQTT_PUBLISH_URL': project_config['MQTT_PUBLISH_URL'],
        'LWM2M_PUBLISH_URL': project_config['LWM2M_PUBLISH_URL'],
        'MQTT_CALLBACK_URL': project_config['MQTT_CALLBACK_URL'],
        'LWM2M_CALLBACK_URL': project_config['LWM2M_CALLBACK_URL'],
        'GATEWAY_CALLBACK_URL': project_config['GATEWAY_CALLBACK_URL'],
        'LWM2M_SUB_CALLBACK_URL': lwm2m_sub_callback_url
    }
    return emqx_config


def _task_config(project_config):
    """ publish, excel task config """

    task_scheduler_node = project_config['TASK_SCHEDULER_NODE']
    task_config = {
        'TASK_SCHEDULER_URL': f"http://{task_scheduler_node}/api/v1/publish_tasks",
        'IMPORT_EXCEL_TASK_URL': f"http://{task_scheduler_node}/api/v1/import_tasks",
        'EXPORT_EXCEL_TASK_URL': f"http://{task_scheduler_node}/api/v1/export_tasks"
    }
    return task_config
