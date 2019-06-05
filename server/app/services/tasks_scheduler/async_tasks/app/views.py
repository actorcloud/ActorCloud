import asyncpg
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from actor_libs.database.async_db import db
from actor_libs.tasks.backend import store_task
from .config import project_config
from .emqx import device_publish_task, device_auth, backend_callback
from .excels import devices_export_task, devices_import_task
from .extra import (
    ActorBackgroundTask, HttpException,
    validate_request_json, validate_request_form
)


app = Starlette()


@app.on_event('startup')
async def open_database_connection_poll():
    _pool = await asyncpg.create_pool(
        host=project_config.get('POSTGRES_HOST', 'localhost'),
        port=project_config.get('POSTGRES_PORT', 5432),
        user=project_config.get('POSTGRES_USER', 'actorcloud'),
        password=project_config.get('POSTGRES_PASSWORD', 'public'),
        database=project_config.get('POSTGRES_DATABASE', 'actorcloud'),
        min_size=5, max_size=10
    )
    await db.open(_pool)


@app.on_event('shutdown')
async def close_database_connection_poll():
    await db.close()


@app.exception_handler(HttpException)
async def http_exception(request: Request, exc: HttpException):
    _json = {
        'errorCode': exc.error_code,
        'message': exc.message,
        'errors': {
            exc.field: exc.message
        }
    }
    return JSONResponse(_json, status_code=exc.code)


@app.route('/api/v1/import_excels', methods=['POST'])
async def import_excels(request: Request):
    request_dict = await validate_request_json(request)
    if not request_dict.get('language'):
        raise HttpException(code=404)
    task_id = await store_task(devices_import_task, func_args=request_dict)
    request_dict['taskID'] = task_id
    task = ActorBackgroundTask(devices_import_task, request_dict)
    record = {'status': 3, 'taskID': task_id}
    return JSONResponse(record, background=task)


@app.route('/api/v1/export_excels', methods=['POST'])
async def export_excels(request):
    request_dict = await validate_request_json(request)
    if not request_dict.get('language'):
        raise HttpException(code=404)
    task_id = await store_task(devices_import_task, func_args=request_dict)
    request_dict['taskID'] = task_id
    task = ActorBackgroundTask(devices_export_task, request_dict)
    record = {'status': 3, 'taskID': task_id}
    return JSONResponse(record, background=task)


@app.route('/api/v1/device_publish', methods=['POST'])
async def device_publish_view(request):
    request_dict = await validate_request_json(request)
    result = await device_publish_task(request_dict)
    return JSONResponse(result)


@app.route('/api/v1/emqx/auth', methods=['POST'])
async def device_auth_view(request):
    request_dict = await validate_request_form(request)
    result, code = await device_auth(request_dict)
    return JSONResponse(result, status_code=code)


@app.route('/api/v1/emqx/callback', methods=['POST'])
async def backend_callback_view(request):
    request_dict = await validate_request_json(request)
    result, code = await backend_callback(request_dict)
    return JSONResponse(result, status_code=code)
