from datetime import datetime
from typing import List, Dict

from flask import g, request
from sqlalchemy import asc, desc, inspect, or_
from sqlalchemy.sql.sqltypes import Integer, String

from actor_libs.cache import Cache
from actor_libs.errors import ParameterInvalid


def dumps_query_result(query_result, **kwargs):
    """ Dump a query result """

    record = {}
    if query_result.__class__.__name__ == 'result':
        query_result_dict = mapping_result(query_result)
        for key, value in query_result_dict.items():
            # When query has with_entities
            if hasattr(value, '__tablename__'):
                schema = get_model_schema(value.__class__.__name__)
                dump_dict = schema.dump(value).data
                record.update(dump_dict)
            elif isinstance(value, datetime):
                record[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                record[key] = value
    else:
        schema = get_model_schema(query_result.__class__.__name__)
        record = schema.dump(query_result).data
    if kwargs.get('code_list'):
        record = dict_code_label(record, kwargs['code_list'])
    return record


def dumps_query_results(query_results: List, **kwargs):
    """ Dump multiple query results """

    records = []
    records_append = records.append
    for query_result in query_results:
        record = dumps_query_result(query_result)
        if kwargs.get('code_list'):
            record = dict_code_label(record, kwargs['code_list'])
        records_append(record)
    return records


def paginate(query, code_list=None):
    """ Result display by paging of query """

    page = request.args.get('_page', 1, type=int)
    limit = request.args.get('_limit', 10, type=int)
    limit = 1000 if limit > 1000 else limit
    offset = (page - 1) * limit if (page - 1) * limit > 0 else 0
    if request.args.get('paginate', type=str) == 'false':
        query_results = query.limit(10000).all()
        page, limit = 0, 10000
    else:
        query_results = query.limit(limit).offset(offset).all()
    # paginate items count
    if page == 1 and len(query_results) < limit:
        total_count = len(query_results)
    else:
        total_count = query.order_by(None).count()
    records = dumps_query_results(query_results, code_list=code_list)
    meta = {'page': page, 'limit': limit, 'count': total_count}  # build paginate schema
    result = {'items': records, 'meta': meta}
    return result


def sort_query(model, query):
    """ sort query """

    order = request.args.get('_order', 'desc', type=str)
    sort_key = request.args.get('_sort', type=str)
    if sort_key:
        sort_key = sort_key
    elif hasattr(model, 'createAt'):
        sort_key = 'createAt'
    elif hasattr(model, 'msgTime'):
        sort_key = 'msgTime'
    if hasattr(model, sort_key):
        if order == 'asc':
            query = query.order_by(asc(getattr(model, sort_key)))
        else:
            query = query.order_by(desc(getattr(model, sort_key)))
    return query


def base_filter_tenant(model, query, tenant_uid):
    """ Filter tenant """

    if not tenant_uid:
        tenant_uid = g.get('tenant_uid')
    exclude_models = ['Message', 'Lwm2mObject', 'Lwm2mItem']
    if model.__name__ in exclude_models or not tenant_uid:
        # admin user not filter
        return query

    if hasattr(model, 'userIntID'):
        from app.models import User

        mapper = inspect(User)
        # inspect model is join user query
        if mapper not in query._join_entities:
            query = query.join(User, User.id == model.userIntID)
        query = query.filter(User.tenantID == tenant_uid)
    elif hasattr(model, 'tenantID'):
        if model.__name__ == 'Role':
            from app.models import Role

            query = query.filter(or_(Role.tenantID == tenant_uid, Role.isShare == 1))
        else:
            query = query.filter(model.tenantID == tenant_uid)
    return query


def filter_api(model, query):
    """ Filter by application """

    exclude_models = []
    app_uid = g.get('app_uid')
    if any([
        not app_uid, model.__name__ in exclude_models
    ]):
        return query
    group_uid_attr = hasattr(model, 'groupID')
    device_uid_attr = hasattr(model, 'deviceID')
    device_id_attr = hasattr(model, 'deviceIntID')
    if not any([group_uid_attr, device_uid_attr, device_id_attr]):
        return query

    from app.models import ApplicationGroup, Group, GroupDevice, Device

    app_groups = Group.query \
        .join(ApplicationGroup, ApplicationGroup.c.groupID == Group.groupID) \
        .filter(Group.userIntID == g.user_id) \
        .with_entities(Group.groupID).all()
    if group_uid_attr:
        query = query.filter(model.groupID.in_(app_groups))
    elif device_uid_attr:
        devices_uid = Device.query \
            .join(GroupDevice, GroupDevice.c.deviceIntID == Device.id) \
            .filter(GroupDevice.c.groupID.in_(app_groups)) \
            .with_entities(Device.deviceID).all()
        query = query.filter(model.deviceID.in_(devices_uid))
    elif device_id_attr:
        devices_id = Device.query \
            .join(GroupDevice, GroupDevice.c.deviceIntID == Device.id) \
            .filter(GroupDevice.c.groupID.in_(app_groups)) \
            .with_entities(Device.id).all()
        query = query.filter(model.deviceIntID.in_(devices_id))
    return query


def filter_group(model, query):
    """ Filter by group """

    exclude_models = []
    user_auth_type = g.get('user_auth_type')
    if any([
        not user_auth_type, user_auth_type == 1,
        model.__name__ in exclude_models
    ]):
        return query
    group_uid_attr = hasattr(model, 'groupID')
    device_uid_attr = hasattr(model, 'deviceID')
    device_id_attr = hasattr(model, 'deviceIntID')
    if not any([group_uid_attr, device_uid_attr, device_id_attr]):
        return query

    from app.models import UserGroup, GroupDevice, Device, Group

    user_groups = Group.query \
        .join(UserGroup, UserGroup.c.groupID == Group.groupID) \
        .filter(UserGroup.c.userIntID == g.user_id) \
        .with_entities(Group.groupID).all()
    if group_uid_attr:
        query = query.filter(model.groupID.in_(user_groups))
    elif device_uid_attr:
        devices_uid = Device.query \
            .join(GroupDevice, GroupDevice.c.deviceIntID == Device.id) \
            .filter(GroupDevice.c.groupID.in_(user_groups)) \
            .with_entities(Device.deviceID).all()
        query = query.filter(model.deviceID.in_(devices_uid))
    elif device_id_attr:
        devices_id = Device.query \
            .join(GroupDevice, GroupDevice.c.deviceIntID == Device.id) \
            .filter(GroupDevice.c.groupID.in_(user_groups)) \
            .with_entities(Device.id).all()
        query = query.filter(model.deviceIntID.in_(devices_id))
    return query


def filter_request_args(model, query):
    """ Query by request args """

    exclude_args = [
        '_page', '_limit', 'paginate', '_sort', '_order', 'startTime',
        'endTime', 'createAt', 'msgTime', 'password', 'token', 'id',
        'userIntID', 'tenantID'
    ]

    for key, value in request.args.items():
        if any([key in exclude_args, value == '', value is None]):
            continue
        elif key.endswith('_like'):
            # 相似类型查询
            key = key.replace('_like', '')
            if hasattr(model, key) and key not in exclude_args:
                column = getattr(model, key)
                if not check_column_type(column, value):
                    continue
                query = query.filter(column.ilike(u'%{0}%'.format(value)))
        elif key.endswith('_in'):
            # 范围查询
            key = key.replace('_in', '')
            try:
                in_value_list = [int(row) for row in value.split(',')]
            except Exception:
                raise ParameterInvalid(field=key)
            if hasattr(model, key) and key not in exclude_args:
                column = getattr(model, key)
                if not check_column_type(column, value):
                    continue
                query = query.filter(column.in_(in_value_list))
        elif key == 'time_name' and value in ['startTime', 'endTime', 'createAt', 'msgTime']:
            start_time = request.args.get('start_time')
            end_time = request.args.get('end_time')
            query = query.filter(getattr(model, value).between(start_time, end_time))
        elif hasattr(model, key):
            column = getattr(model, key)
            if not check_column_type(column, value):
                continue
            query = query.filter(column == value)
        else:
            continue
    return query


def mapping_result(query_result):
    convert_dict = {
        key: getattr(query_result, key)
        for key in query_result.keys()
    }
    return convert_dict


def dict_code_label(record: Dict, code_list: List = None):
    """ Convert dict_code """

    cache = Cache()
    dict_code_cache = cache.dict_code
    if not dict_code_cache:
        return record

    for code in code_list:
        if record.get(code) is None or not dict_code_cache.get(code):
            continue
        code_value_dict = dict_code_cache[code]
        code_value = record[code]
        if code_value_dict.get(code_value):
            record[f'{code}Label'] = code_value_dict[code_value].get(f'{g.language}Label')
        else:
            record[f'{code}Label'] = None
    return record


def get_model_schema(model_name):
    cache = Cache()
    models_schema_cache = cache.models_schema_cache
    if models_schema_cache.get(model_name):
        model_schema = models_schema_cache[model_name]
    else:
        from app import schemas

        schema_name = f"{model_name}Schema"
        if hasattr(schemas, schema_name):
            model_schema = getattr(schemas, schema_name)()
            cache.models_schema_cache[model_name] = model_schema
        else:
            model_schema = None
    return model_schema


def check_column_type(model_column, value):
    value_type = type(value)
    column_type = type(model_column.type)
    status = False
    if value_type == int and issubclass(column_type, Integer):
        status = True
    elif value_type == str:
        if value.isdigit() and issubclass(column_type, Integer):
            status = True
        elif issubclass(column_type, String):
            status = True
    return status
