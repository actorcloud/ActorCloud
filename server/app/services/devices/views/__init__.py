from flask import Blueprint


bp = Blueprint('devices', __name__)

from . import auth  # noqa: E402
from . import devices  # noqa: E402
from . import device_events  # noqa: E402
from . import device_security  # noqa: E402
from . import emq_select  # noqa: E402
from . import groups  # noqa: E402
from . import lwm2m  # noqa: E402
from . import overview  # noqa: E402
from . import security  # noqa: E402
from . import gateways  # noqa: E402
from . import publish  # noqa: E402
from . import tags  # noqa: E402
from . import timer_publish  # noqa: E402


__all__ = [
    'bp', 'auth', 'devices', 'device_events', 'device_security', 'emq_select', 'groups', 'lwm2m',
    'overview', 'security', 'gateways', 'publish', 'tags', 'timer_publish'
]
