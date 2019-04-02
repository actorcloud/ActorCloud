from flask import Blueprint


bp = Blueprint('alerts', __name__)

from . import alerts  # noqa: E402


__all__ = ['bp', 'alerts']
