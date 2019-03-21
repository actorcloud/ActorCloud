from flask import g, abort
from flask_sqlalchemy import BaseQuery
from sqlalchemy import inspection

from actor_libs.errors import DataNotFound
from database.orm.utils import (
    model_tenant_query, paginate, model_api_query, model_tag_auth_query,
    args_query, sort_query, result_to_dict
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
        query = self
        query = model_tenant_query(model, query)
        if g.get('app_uid'):
            # filter api
            query = model_api_query(model, query)
        else:
            # filter tag
            query = model_tag_auth_query(model, query)
        return query

    def first_or_404(self):
        query = self.filter_tenant()
        rv = query.first()
        if rv is None:
            abort(404)
        return rv

    def to_dict(self, **kwargs):
        """
        Query result to dict with schema
        """
        model = self._get_query_model()
        query_result = self.first_or_404()
        record = result_to_dict(model, query_result, **kwargs)
        return record

    def pagination(self, code_list=None):
        model = self._get_query_model()
        return paginate(model, self, code_list)

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
