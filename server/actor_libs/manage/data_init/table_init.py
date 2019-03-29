import hashlib
import os
from typing import List

import yaml
from flask import current_app
from sqlalchemy import text

from actor_libs.database.orm import db
from actor_libs.utils import get_cwd, get_services_path
from app.models import (
    DictCode, SystemInfo, User, Resource
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


def init_resources() -> None:
    """Initialize resources table """

    level1, level2, level3, level4 = [], [], [], []
    services_path = get_services_path().values()
    for service_path in services_path:
        resource_path = os.path.join(service_path, 'resources.yml')
        if not os.path.isfile(resource_path):
            continue
        else:
            with open(resource_path, 'r', encoding='utf-8') as load_file:
                resource_data = yaml.load(load_file)
            if not resource_data:
                continue
            for _, value in resource_data.items():
                if value.get('level') == 1:
                    level1.append(value)
                elif value.get('level') == 2:
                    level2.append(value)
                elif value.get('level') == 3:
                    level3.append(value)
                else:
                    level4.append(value)

    all_levels_resources = [level1, level2, level3, level4]
    for level_resources in all_levels_resources:
        _insert_resources(level_resources=level_resources)
    info = "resources successfully!"
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


def _insert_resources(level_resources: List = None) -> None:
    """ insert resources to database """

    insert_resources_code = [
        level_resource.get('code') for level_resource in level_resources
    ]
    query_resources = db.session.query(Resource.code, Resource).all()
    query_resources_dict = dict(query_resources)
    query_resources_code = query_resources_dict.keys()
    insert_code = set(insert_resources_code) ^ set(query_resources_code)
    update_code = set(insert_resources_code) & set(query_resources_code)

    for level_resource in level_resources:
        level_code = level_resource.get('code')
        if level_code in insert_code:
            resource = Resource()
            for key, value in level_resource.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
                db.session.add(resource)
        elif level_code in update_code and query_resources_dict.get(level_code):
            query_resource = query_resources_dict.get(level_code)
            for key, value in level_resource.items():
                if hasattr(query_resource, key):
                    setattr(query_resource, key, value)
        else:
            raise RuntimeError(f'Please check {level_resource}')
    db.session.commit()
