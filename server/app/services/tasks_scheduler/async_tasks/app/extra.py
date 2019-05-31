from typing import Callable, Any, Dict

from starlette.background import BackgroundTask
from starlette.requests import Request

from actor_libs.types.exceptions import ExceptionT
from actor_libs.utils import generate_uuid


CODE_ERROR_DICT = {
    400: 'BAD_REQUEST',
    401: 'AUTH_FAILED',
    404: 'DATA_NOT_FOUND',
    403: 'RESOURCE_LIMITED',
    500: 'INTERNAL_ERROR'
}
CODE_MESSAGE_DICT = {
    400: 'Bad request',
    401: 'Auth failed',
    404: 'Not found',
    403: 'Resource limited',
    500: 'Internal error'
}


class ActorBackgroundTask(BackgroundTask):
    taskID = generate_uuid()

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        super().__init__(func, *args, **kwargs)


class HttpException(ExceptionT):

    def __init__(self, code, *, field=None):
        self.code = code
        self.error_code = CODE_ERROR_DICT.get(code, 'STARLETTE_ERROR')
        self.message = CODE_MESSAGE_DICT.get(code, 'Starlette error')
        self.field = field or 'url'


async def validate_request_json(request: Request) -> Dict:
    try:
        request_dict = await request.json()
    except Exception:
        raise HttpException(code=400)
    if not request_dict:
        raise HttpException(code=400)
    return request_dict


async def validate_request_form(request: Request) -> Dict:
    try:
        request_form = await request.form()
        request_dict = dict(request_form)
    except Exception:
        raise HttpException(code=400)
    if not request_dict:
        raise HttpException(code=400)
    return request_dict
