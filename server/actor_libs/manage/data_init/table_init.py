import hashlib
import os
from typing import List, Tuple
from xml.etree import cElementTree as ETree

import yaml
from flask import current_app
from sqlalchemy import text

from actor_libs.database.orm import db
from actor_libs.utils import get_cwd, get_services_path
from app.models import (
    DictCode, SystemInfo, User, Resource, Service,
    Lwm2mObject, Lwm2mItem
)


__all__ = [
    'convert_timescaledb', 'init_services',
    'init_resources', 'init_admin_account', 'init_dict_code',
    'init_system_info', 'init_lwm2m_info'
]


def convert_timescaledb():
    """ timescaledb process """

    timescaledb_init = """
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    """

    emqx_bills = """
    SELECT create_hypertable('emqx_bills', 'msgTime');
    """

    emqx_bills_hour = """
    SELECT create_hypertable('emqx_bills_hour', 'countTime');
    """

    device_events = """
    SELECT create_hypertable('device_events', 'msgTime');
    """

    data_point_event_hour = """
    SELECT create_hypertable('data_point_event_hour', 'countTime');
    """

    lwm2m_event_hour = """
    SELECT create_hypertable('lwm2m_event_hour', 'countTime');
    """

    client_connect_logs = """
    SELECT create_hypertable('connect_logs', 'msgTime');
    """

    with db.engine.begin() as connection:
        connection.execute(timescaledb_init)
        connection.execute(emqx_bills)
        connection.execute(emqx_bills_hour)
        connection.execute(device_events)
        connection.execute(data_point_event_hour)
        connection.execute(lwm2m_event_hour)
        connection.execute(client_connect_logs)


def init_services() -> None:
    """ services table init """

    project_backend = get_cwd()
    service_path = os.path.join(project_backend, 'config/base/services.yml')
    if not os.path.isfile(service_path):
        raise RuntimeError(f"The file {service_path} does not exist.")
    with open(service_path, 'r', encoding='utf-8') as load_file:
        service_data = yaml.load(load_file)

    query_service_dict = dict(
        db.session.query(Service.code, Service).all()
    )
    for code, service_values in service_data.items():
        if query_service_dict.get(code):
            query_service = query_service_dict.get(code)
            for key, value in service_values.items():
                if hasattr(query_service, key):
                    setattr(query_service, key, value)
        else:
            service = Service()
            for key, value in service_values.items():
                if hasattr(service, key):
                    setattr(service, key, value)
                db.session.add(service)
    db.session.commit()
    info = "services table init successfully!"
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


def init_lwm2m_info() -> None:
    """ Initialize lwm2m_object and lwm2m_item table """

    project_backend = current_app.config['PROJECT_PATH']
    lwm2m_xml_dir_path = os.path.join(project_backend, 'config/base/lwm2m_obj')
    if not os.path.isdir(lwm2m_xml_dir_path):
        raise RuntimeError(f"no such file or directory: lwm2m_xml_dir_path")

    query_lwm2m_object = db.session.query(Lwm2mObject.objectID).all()
    query_lwm2m_object_list = [i[0] for i in query_lwm2m_object]
    query_lwm2m_items = db.session.query(Lwm2mItem.itemID, Lwm2mObject.objectID).all()

    object_list, item_list = _parse_lwm2m_file(xml_path=lwm2m_xml_dir_path)
    for lwm2m_object in object_list:
        if int(lwm2m_object.get('ObjectID')) in query_lwm2m_object_list:
            continue
        insert_lwm2m_object = Lwm2mObject(
            objectID=lwm2m_object.get('ObjectID'),
            objectName=lwm2m_object.get('Name'),
            description=lwm2m_object.get('Description1'),
            objectURN=lwm2m_object.get('ObjectURN'),
            mandatory=lwm2m_object.get('Mandatory'),
            objectVersion=lwm2m_object.get('ObjectVersion'),
            multipleInstance=lwm2m_object.get('MultipleInstances'))
        db.session.add(insert_lwm2m_object)
    db.session.flush()

    for lwm2m_item in item_list:
        # is exist jump
        item_id_tuple = (
            int(lwm2m_item.get('ID')), int(lwm2m_item.get('ObjectID'))
        )
        if item_id_tuple in query_lwm2m_items:
            continue
        insert_lwm2m_item = Lwm2mItem(
            objectID=lwm2m_item.get('ObjectID'),
            itemID=lwm2m_item.get('ID'),
            objectItem=f'/{lwm2m_item.get("ObjectID")}/{lwm2m_item.get("ID")}',
            itemName=lwm2m_item.get('Name'),
            description=lwm2m_item.get('Description'),
            itemType=lwm2m_item.get('Type'),
            itemOperations=lwm2m_item.get('Operations'),
            itemUnit=lwm2m_item.get('Units'),
            mandatory=lwm2m_item.get('Mandatory'),
            rangeEnumeration=lwm2m_item.get('RangeEnumeration'),
            multipleInstance=lwm2m_item.get('MultipleInstances'))
        db.session.add(insert_lwm2m_item)
    db.session.commit()
    info = "lwm2m_object lwm2m_item table init successfully!"
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


def _parse_lwm2m_file(xml_path: str) -> Tuple[list, list]:
    """
    read lwm2m object and resource item in  lwm2m xml file
    :param xml_path: lwm2m object xml file path
    """

    file_names = [
        f"{xml_path}/{file_name}" for file_name in os.listdir(xml_path)
        if file_name.endswith('.xml')
    ]

    object_list = []
    item_list = []
    object_append = object_list.append
    item_extend = item_list.extend
    for xml_file in file_names:
        object_dict, items = _lw2m_xml_to_dict(xml_file)
        object_append(object_dict)
        item_extend(items)
    return object_list, item_list


def _lw2m_xml_to_dict(xml_file: str) -> Tuple[dict, list]:
    """
    Converting lwm2m xml object to dict
    :param xml_file: lwm2m object xml file
    :return: object dict, resource dict list
    """

    root = ETree.ElementTree(file=xml_file)
    lwm2m_object = root.find('Object')
    object_id = lwm2m_object.findtext('ObjectID')
    object_dict = {}
    for child in lwm2m_object:
        object_dict[child.tag] = child.text
    resources = lwm2m_object.iterfind('Resources/Item')
    items = []
    items_append = items.append
    for resource in resources:
        item_id = resource.attrib.get('ID')
        item_dict = {'ID': item_id, 'ObjectID': object_id}
        for item in resource:
            item_dict[item.tag] = item.text
        items_append(item_dict)
    return object_dict, items
