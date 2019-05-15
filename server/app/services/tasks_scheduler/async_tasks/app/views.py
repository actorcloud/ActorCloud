from typing import Any

from faust.web import Request, Response, View

from . import faust_app
from .tasks import excel_export_task, excel_import_task, device_publish_task
from .validate import validate_request


@faust_app.page('/api/v1/publish_tasks')
class PublishTask(View):
    async def post(self, request: Request, **kwargs: Any) -> Response:
        request_json = await validate_request(request, request_type='publish')
        task_id = request_json.get('taskID')  # task scheduler ID

        await device_publish_task.delay(
            task_id=task_id, request_json=request_json
        )
        response = {'taskID': task_id}
        return self.json(response)


@faust_app.page('/api/v1/export_tasks')
class ExportTask(View):
    async def post(self, request: Request, **kwargs: Any) -> Response:
        request_json = await validate_request(request, request_type='excel')
        task_id = request_json.get('taskID')
        response = await excel_export_task.delay(task_id=task_id, request_json=request_json)
        return self.json(response)


@faust_app.page('/api/v1/import_tasks')
class ImportTak(View):
    async def post(self, request: Request, **kwargs: Any) -> Response:
        request_json = await validate_request(request, request_type='excel')
        task_id = request_json.get('taskID')
        response = await excel_import_task.delay(task_id=task_id, request_json=request_json)
        return self.json(response)
