import hashlib
import os

import yaml
from flask import current_app
from sqlalchemy import text

from actor_libs.database.orm import db
from actor_libs.utils import get_cwd
from app.models import (
    DictCode, SystemInfo, User
)


__all__ = [
    'init_system_info', 'init_admin_account', 'init_dict_code'
]


def init_system_info() -> None:
    """ Initialize system info table """

    system_info_key = (
        'mqttBroker', 'mqttsBroker', 'mqttssBroker', 'coapBroker',
        'coapsBroker', 'coapssBroker', 'wsBroker', 'wssBroker',
        'projectVersion'
    )
    query = db.session.query(SystemInfo.key).all()
    is_exist_keys = [key[0] for key in query]
    for key in system_info_key:
        if key in is_exist_keys:
            continue
        new_system_info = SystemInfo(key=key)
        db.session.add(new_system_info)
    db.session.commit()
    info = "system info table init successfully!"
    print(info)


def init_admin_account() -> None:
    """ Initialize admin user """

    email = current_app.config.get('ADMIN_EMAIL', 'admin@actorcloud.io')
    password = current_app.config.get('ADMIN_PASSWORD', '123456').encode('utf-8')
    admin_user = User(
        username='admin',
        email=email, roleIntID=1,
        password=hashlib.sha256(password).hexdigest()
    )
    db.session.add(admin_user)
    db.session.commit()
    info = "admin user init successfully!"
    print(info)


def init_dict_code() -> None:
    """ Initialize dict code table """

    project_backend = get_cwd()
    dict_code_path = os.path.join(project_backend, 'config/base/dict_code.yml')
    if not os.path.isfile(dict_code_path):
        raise RuntimeError(f"The file {dict_code_path} does not exist.")
    with open(dict_code_path, 'r', encoding='utf-8') as load_file:
        dict_code_yml = yaml.load(load_file)

    # truncate dict_code table
    truncate_sql = 'TRUNCATE TABLE dict_code RESTART IDENTITY;'
    db.engine.execute(
        text(truncate_sql).execution_options(autocommit=True)
    )
    for _, dict_code_values in dict_code_yml.items():
        for dict_code_value in dict_code_values:
            dict_code = DictCode()
            for key, value in dict_code_value.items():
                if hasattr(dict_code, key):
                    setattr(dict_code, key, value)
                db.session.add(dict_code)
    db.session.commit()
    info = "dict_code table init successfully!"
    print(info)
