from flask import Blueprint


bp = Blueprint('device_data', __name__)

from . import device_events  # noqa: E402
from . import connect_logs  # noqa: E402
from . import capability_data  # noqa: E402


__all__ = [
    'bp', 'device_events', 'connect_logs', 'capability_data'
]
