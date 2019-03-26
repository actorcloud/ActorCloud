from flask import g
from flask_sqlalchemy import BaseQuery
from sqlalchemy import inspection

from actor_libs.errors import DataNotFound
from .utils import (
    base_filter_tenant, filter_api, filter_tag, filter_request_args,
    sort_query, dumps_query_result, paginate, get_model_schema
)


class ExtendQuery(BaseQuery):

    def _get_query_model(self):
        """ Get database model """

        entity = self._mapper_zero()
        insp = inspection.inspect(entity)
        if insp.is_selectable:
            entity = insp.c
        elif insp.is_aliased_class:
            entity = insp.entity
        elif hasattr(insp, "mapper"):
            entity = insp.mapper.class_
        else:
            pass
        return entity

    def filter_tenant(self):
        """ Filter tenant"""

        model = self._get_query_model()
        query = base_filter_tenant(model, self)
        if g.get('app_uid'):
            query = filter_api(model, query)  # filter api
        else:
            query = filter_tag(model, query)  # filter tag
        return query

    def first_or_404(self):
        query = self.filter_tenant()
        result = query.first()
        if result is None:
            raise DataNotFound()
        return result

    def to_dict(self, **kwargs):
        """ Query result to dict with schema """

        model = self._get_query_model()
        query_result = self.first_or_404()
        model_schema = get_model_schema(model.__name__)
        record = dumps_query_result(model_schema, query_result, **kwargs)
        return record

    def pagination(self, code_list=None):
        model = self._get_query_model()
        query = self.filter_tenant()  # filter tenant
        query = sort_query(model=model, query=query)  # sort query
        query = filter_request_args(model=model, query=query)  # filter request args
        model_schema = get_model_schema(model.__name__)
        return paginate(model_schema, query, code_list)

    def select_options(self, attrs: list = None, is_limited=True):
        """
        Return emq_select record
        :param attrs: attr list
        :param is_limited: Whether to limit the database results,limit 10 records if False
        :return: records
        """
        model = self._get_query_model()
        query = self.filter_tenant()
        query = args_query(model, query)
        query = sort_query(model, query)

        if is_limited:
            results = query.limit(10).all()
        else:
            results = query.all()
        records = []
        for result in results:
            record = {
                'label': result.label,
                'value': result.value
            }
            if attrs:
                record_attr = {}
                for attr in attrs:
                    record_attr[attr] = getattr(result, attr)
                record['attr'] = record_attr
            records.append(record)

        return records

    def many(self, limit: int = None, allow_none=True):
        query = self.filter_tenant()
        if limit:
            query = query.limit(limit)
        result = query.all()

        if not allow_none and not result:
            raise DataNotFound(field='url')

        return result
