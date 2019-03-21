# coding: utf-8

from __future__ import absolute_import

from datetime import datetime
from typing import List, Dict

from flask import current_app, g, request
from sqlalchemy import asc, desc, inspect, or_

from actor_libs.actor_typedefs import CacheDictCode
from actor_libs.errors import ParameterInvalid


def sort_query(model, query):
    """
    sort query
    :param model: model class
    :param query: base database
    :return: query
    """
    sort_key = request.args.get('_sort', 'createAt', type=str)
    order = request.args.get('_order', 'desc', type=str)

    if hasattr(model, sort_key):
        if order == 'asc':
            query = query.order_by(asc(getattr(model, sort_key)))
        else:
            query = query.order_by(desc(getattr(model, sort_key)))
    return query


def model_tenant_query(model, query):
    """
    Filter tenant
    :param model: model class
    :param query: query
    :return: query
    """

    exclude_models = ['Message', 'Lwm2mObject', 'Lwm2mItem']
    if model.__name__ in exclude_models or not g.get('tenant_uid'):
        return query

    if hasattr(model, 'userIntID'):
        from microservices.models import User

        mapper = inspect(User)
        # 判断是否已经 join，防止重复 join
        if mapper not in query._join_entities:
            query = query.join(User, User.id == model.userIntID)
        query = query.filter(User.tenantID == g.tenant_uid)
    elif hasattr(model, 'tenantID'):
        if model.__name__ == 'Role':
            from microservices.models import Role
            query = query.filter(or_(Role.tenantID == g.tenant_uid, Role.isShare == 1))
        else:
            query = query.filter(model.tenantID == g.tenant_uid)
    return query


def args_query(model, query):
    """
    Query by request args
    :param model: model class
    :param query: BaseQuery
    :return: BaseQuery
    """

    exclude_args = [
        '_page', '_limit', 'paginate', '_sort', '_order',
        'startTime', 'endTime', 'createAt', 'msgTime',
        'password', 'token', 'id', 'userIntID', 'tenantID'
    ]

    for key, value in request.args.items():
        if any([key in exclude_args, value == '', value is None]):
            continue
        elif key.endswith('_like'):
            # 相似类型查询
            key = key.replace('_like', '')
            if hasattr(model, key) and key not in exclude_args:
                query = query \
                    .filter(getattr(model, key).ilike(u'%{0}%'.format(value)))
        elif key.endswith('_in'):
            # 范围查询
            key = key.replace('_in', '')
            try:
                in_value_list = [int(row) for row in value.split(',')]
            except Exception:
                raise ParameterInvalid(field=key)
            if hasattr(model, key) and key not in exclude_args:
                query = query.filter(getattr(model, key).in_(in_value_list))
        elif (key == 'time_name' and
              value in ['startTime', 'endTime', 'createAt', 'msgTime']):
            # 开始或结束时间查询
            start_time = request.args.get('start_time')
            end_time = request.args.get('end_time')
            query = query.filter(getattr(model, value).between(start_time, end_time))
        elif hasattr(model, key):
            query = query.filter(getattr(model, key) == value)
        else:
            continue
    return query


def dumps_result(schema, query_result):
    """
    Dump query result by schema
    :param schema: schema
    :param query_result: query result
    :return: record
    """

    record = {}
    # When query has with_entities
    schema_name = schema.__class__.__name__
    if query_result.__class__.__name__ == 'result':
        query_result_dict = result_convert_dict(query_result)
        for key, value in query_result_dict.items():
            if schema_name.startswith(value.__class__.__name__):
                schema_dict = schema.dump(value).data
                record.update(schema_dict)
            elif isinstance(value, datetime):
                record[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                record[key] = value
    else:
        record, _ = schema.dump(query_result).data
    return record


def model_dumps_results(model, query_results, code_list=None):
    """
    Dump query result
    :param code_list: dict code list to be converted
    :param model: model name
    :param query_results: query result list
    :return: records list
    """

    # dynamic import
    current_schema_name = model.__name__ + 'Schema'
    current_schema = getattr(current_app.schemas, current_schema_name)
    schema = current_schema()

    if code_list:
        from microservices import sync_cache

        dict_code_cache = sync_cache.dict_code
    else:
        dict_code_cache = {}

    records = []
    records_append = records.append
    for query_result in query_results:
        record = dumps_result(schema, query_result)
        record = record_dict_code_convert(
            record, code_list=code_list,
            dict_code_cache=dict_code_cache
        )
        records_append(record)
    return records


def result_convert_dict(query_result):
    """
    Convert query result to dict
    :param query_result: query result
    :return: convert_dict
    """
    convert_dict = {
        key: getattr(query_result, key) for key in query_result.keys()
    }
    return convert_dict


def record_dict_code_convert(record: Dict,
                             code_list: List = None,
                             dict_code_cache: CacheDictCode = None):
    """
    Convert dict_code
    :param dict_code_cache:
    :param code_list: dict code list to be converted
    :param record
    """

    if not dict_code_cache or not code_list:
        return record

    for code in code_list:
        if record.get(code) is None or not dict_code_cache.get(code):
            continue
        code_value_dict = dict_code_cache[code]
        code_value = record[code]
        if code_value_dict.get(code_value):
            record[f'{code}Label'] = code_value_dict[code_value]
        else:
            record[f'{code}Label'] = None
    return record


def paginate(model, query, code_list=None):
    page = request.args.get('_page', 1, type=int)
    limit = request.args.get('_limit', 10, type=int)
    limit = 1000 if limit > 1000 else limit

    # filter request args
    query = args_query(model=model, query=query)
    # filter tenant
    query = model_tenant_query(model=model, query=query)
    if g.get('app_uid'):
        # filter api
        query = model_api_query(model=model, query=query)
    else:
        # filter tag auth
        query = model_tag_auth_query(model=model, query=query)
    # sort query
    query = sort_query(model=model, query=query)
    # paginate
    offset = (page - 1) * limit if (page - 1) * limit > 0 else 0
    if request.args.get('paginate', type='str') == 'false':
        query_results = query.limit(10000).all()
    else:
        query_results = query.limit(limit).offset(offset).all()
    # paginate items count
    if page == 1 and len(query_results) < limit:
        total_count = len(query_results)
    else:
        total_count = query.order_by(None).count()

    records = model_dumps_results(
        model=model, query_results=query_results,
        code_list=code_list
    )
    # build paginate
    meta = {'page': page, 'limit': limit, 'count': total_count}
    result = {'items': records, 'meta': meta}
    return result


def model_api_query(model, query):
    """
    Filter by application
    :param model: model class
    :param query: query
    :return: query
    """

    exclude_models = ['Application', 'Gateway']
    app_uid = g.get('app_uid')

    if any([not app_uid, model.__name__ in exclude_models,
            not (hasattr(model, 'productIntID') or
                 hasattr(model, 'productID'))]):
        return query

    from microservices.models import Application, Product
    application = Application.query \
        .filter(Application.appID == app_uid).first_or_404()
    if hasattr(model, 'productIntID'):
        products_id = application.products.with_entities(Product.id).all()
        query = query.filter(getattr(model, 'productIntID').in_(set(products_id)))
    elif hasattr(model, 'productID'):
        products_uid = application.products \
            .with_entities(Product.productID).all()
        query = query.filter(getattr(model, 'productID').in_(set(products_uid)))
    return query


def model_tag_auth_query(model, query):
    """
    Filter by tag
    :param model: model
    :param query: query
    :return: query
    """

    exclude_models = []
    user_auth_type = g.get('user_auth_type')
    if any([
        not user_auth_type, user_auth_type == 1,
        model.__name__ in exclude_models
    ]):
        return query

    tag_uid_attr = hasattr(model, 'tagID')
    device_uid_attr = hasattr(model, 'deviceID')
    device_id_attr = hasattr(model, 'deviceIntID')

    if not any([tag_uid_attr, device_uid_attr, device_id_attr]):
        return query
    from microservices.models import UserTag, ClientTag, Client, Tag

    user_tags = Tag.query \
        .join(UserTag) \
        .filter(UserTag.c.userIntID == g.user_id) \
        .with_entities(Tag.tagID) \
        .all()

    if tag_uid_attr:
        query = query.filter(model.tagID.in_(set(user_tags)))
    elif device_id_attr:
        tag_devices_id = Tag.query \
            .filter(ClientTag.c.tagID.in_(set(user_tags))) \
            .with_entities(ClientTag.c.deviceIntID) \
            .all()
        query = query.filter(model.deviceIntID.in_(set(tag_devices_id)))
    elif device_uid_attr:
        tag_devices_uid = Client.query \
            .join(ClientTag, ClientTag.c.deviceIntID == Client.id) \
            .filter(ClientTag.c.tagID.in_(set(user_tags))) \
            .with_entities(Client.deviceID) \
            .all()
        query = query.filter(model.deviceID.in_(set(tag_devices_uid)))
    else:
        pass
    return query


def result_to_dict(model, query_result, **kwargs):
    current_schema_name = model.__name__ + 'Schema'
    current_schema = getattr(current_app.schemas, current_schema_name)
    if kwargs.get('only'):
        schema = current_schema(only=kwargs['only'])
    elif kwargs.get('exclude'):
        schema = current_schema(exclude=kwargs['exclude'])
    else:
        schema = current_schema()

    record = dumps_result(schema, query_result)

    if kwargs.get('code_list'):
        from microservices import sync_cache

        dict_code_cache = sync_cache.dict_code
        record = record_dict_code_convert(
            record, code_list=kwargs['code_list'],
            dict_code_cache=dict_code_cache
        )
    return record
