from typing import AnyStr, Union, Tuple, Optional

from flask import request, current_app

from actor_libs.database.orm import db
from actor_libs.errors import ParameterInvalid


__all__ = ['fetch_val', 'fetch_many']


def fetch_val(query_sql: AnyStr) -> Optional[dict]:
    try:
        result = db.engine.execute(query_sql).scalar()
    except Exception as error:
        current_app.logger.error(error)
        result = None
    return result


def fetch_many(query_sql: AnyStr, limit: int = 1000, paginate: bool = True) -> Union[dict, list]:
    """
    Fetch many by SQL
    """
    if paginate:
        query_sql, paginate_meta = _get_paginate_meta(query_sql)
    else:
        query_sql = f'{query_sql} LIMIT {limit}'

    try:
        result = db.engine.execute(query_sql).fetchall()
        records = [dict(row) for row in result]
    except Exception as error:
        current_app.logger.error(error)
        records = []

    if paginate:
        return_records = {
            'meta': paginate_meta,
            'items': records
        }
    else:
        return_records = records

    return return_records


def _get_paginate_meta(query_sql: AnyStr) -> Tuple[str, dict]:
    page = request.args.get('_page', type=int, default=1)
    limit = request.args.get('_limit', type=int, default=10)
    if limit > 500 or limit <= 0:
        raise ParameterInvalid(field='_limit')
    if page < 1:
        raise ParameterInvalid(field='_page')
    offset = (page - 1) * limit

    count_sql = f'SELECT COUNT(*) FROM ({query_sql}) AS query_count'
    try:
        query_count = db.engine.execute(count_sql).scalar()
    except Exception as error:
        current_app.logger.error(error)
        query_count = 0

    paginate_sql = f'{query_sql} LIMIT {limit} OFFSET {offset}'
    paginate_meta = {
        "count": query_count,
        "limit": limit,
        "page": page
    }
    return paginate_sql, paginate_meta
