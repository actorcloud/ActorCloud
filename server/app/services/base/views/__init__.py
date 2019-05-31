from flask import Blueprint


bp = Blueprint('base', __name__)

from . import users  # noqa: E402
from . import auth  # noqa: E402
from . import select_options  # noqa: E402
from . import logs  # noqa: E402
from . import messages  # noqa: E402
from . import roles  # noqa: E402
from . import system  # noqa: E402
from . import tenants  # noqa: E402
from . import tasks  # noqa: E402
from . import file_system  # noqa: E402
from . import overview  # noqa: E402


__all__ = [
    'bp', 'auth', 'select_options', 'logs', 'messages',
    'roles', 'system', 'tenants', 'users', 'tasks', 'overview'
]
