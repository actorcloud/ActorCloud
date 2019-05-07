from flask_sqlalchemy import BaseQuery
from flask_sqlalchemy.model import DefaultMeta

__all__ = ['BaseQueryT', 'BaseModelT']


class BaseQueryT(BaseQuery):
    ...


class BaseModelT(DefaultMeta):
    ...


