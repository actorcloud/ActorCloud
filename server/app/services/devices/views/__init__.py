from flask import Blueprint


bp = Blueprint('devices', __name__)

from . import emqx  # noqa: E402
from . import devices  # noqa: E402
from . import emq_select  # noqa: E402
from . import groups  # noqa: E402
from . import security  # noqa: E402
from . import gateways  # noqa: E402


__all__ = [
    'bp', 'emqx', 'devices',
    'groups', 'security', 'gateways', 'emq_select'
]
