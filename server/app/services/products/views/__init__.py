from flask import Blueprint


bp = Blueprint('products', __name__)

from . import products  # noqa: E402
from . import data_points  # noqa: E402
from . import data_streams  # noqa: E402
from . import stream_points  # noqa: E402
from . import emq_select  # noqa: E402


__all__ = [
   'bp', 'products', 'data_points', 'data_streams', 'stream_points', 'emq_select'
]
