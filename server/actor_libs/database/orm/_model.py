from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import g, request

from ._query import ExtendQuery
from .utils import (
    sort_query, model_tag_auth_query, args_query, result_to_dict, model_api_query,
    model_tenant_query, model_dumps_results
)


db = SQLAlchemy(query_class=ExtendQuery)


class ModelMixin:

    def to_dict(self, **kwargs):
        """
        :param kwargs:
            only:  对查询结果只返回only列表中指定字段, type=list
            exclude: 对查询结果不返回exclude列表中指定字段, type=list
            query_result: 查询结果集 database result type=tuple
            code_list: 需要转换的dict code 列表 type=list
        :return: record type=dict
        """
        model = self.__class__
        result = self
        if kwargs.get('query_result'):
            result = kwargs.pop('query_result')
        return result_to_dict(model, result, **kwargs)

    def create(self, request_dict=None, commit=True):
        if request_dict:
            for key, value in request_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.add(self)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return self

    def update(self, request_dict=None, commit=True):
        if request_dict:
            for key, value in request_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        if commit:
            db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def paginate(cls, query, code_list=None):
        page = request.args.get('_page', 1, type=int)
        limit = request.args.get('_limit', 10, type=int)
        limit = 1000 if limit > 1000 else limit

        # filter request args
        query = args_query(model=cls, query=query)
        # filter tenant
        query = model_tenant_query(model=cls, query=query)
        if g.get('app_uid'):
            # filter api
            query = model_api_query(model=cls, query=query)
        else:
            # filter tag auth
            query = model_tag_auth_query(model=cls, query=query)
        # sorted database
        query = sort_query(model=cls, query=query)
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
        # database result dumps ujson
        records = model_dumps_results(
            model=cls, query_results=query_results,
            code_list=code_list
        )
        # build paginate
        meta = {'page': page, 'limit': limit, 'count': total_count}
        result = {'items': records, 'meta': meta}
        return result


class BaseModel(ModelMixin, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    createAt = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updateAt = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
