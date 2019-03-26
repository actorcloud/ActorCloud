# coding: utf-8

from flask import Blueprint


bp = Blueprint('applications', __name__)

from . import applications  # noqa: E402


__all__ = ['applications']
