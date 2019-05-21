from json.decoder import JSONDecodeError
from typing import Callable, Any, Dict

from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

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

    def _store_task(self):
        ...


class HttpException(ExceptionT):

    def __init__(self, code, *, field=None):
        self.code = code
        self.error_code = CODE_ERROR_DICT.get(code, 'Task_ERROR')
        self.message = CODE_MESSAGE_DICT.get(code, 'Task execute error')
        self.field = field


async def validate_request(request) -> Dict:
    try:
        request_json = await request.json()
    except JSONDecodeError:
        raise HttpException(code=400)
    return request_json
