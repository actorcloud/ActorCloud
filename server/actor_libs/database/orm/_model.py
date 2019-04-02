from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from ._query import ExtendQuery
from .utils import dumps_query_result, get_model_schema


db = SQLAlchemy(query_class=ExtendQuery)


class ModelMixin:

    def to_dict(self, **kwargs):
        model = self.__class__
        result = self
        model_schema = get_model_schema(model.__name__)
        return dumps_query_result(model_schema, result, **kwargs)

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

    def delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()


class BaseModel(ModelMixin, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    createAt = db.Column(db.DateTime, nullable=True, default=datetime.now)
    updateAt = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
