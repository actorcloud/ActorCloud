from ujson import loads as ujson_loads

from typing import AnyStr, Dict
from faust.web import Request

from faust.web.exceptions import WebError


async def validate_request(request: Request, request_type: AnyStr) -> Dict:
    if not request.body_exists:
        raise WebError(code=400, detail='BAD_REQUEST')
    try:
        request_json = await request.json(loads=ujson_loads)
    except ValueError:
        raise WebError(code=400, detail='BAD_REQUEST')
    if not request_json.get('taskID'):
        raise WebError(code=422, detail='taskID')
    if request_type == 'publish':
        request_json = await _validate_publish_request(request_json)
    elif request_type == 'excel':
        request_json = await _validate_excel_request(request_json)
    return request_json


async def _validate_publish_request(request_json):
    publish_type = request_json.get('publishType')
    if publish_type not in [1, 2]:
        raise WebError(code=422, detail='publish_type')
    return request_json


async def _validate_excel_request(request_json):
    return request_json
