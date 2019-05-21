# actorcloud async tasks

* device_publish
* group_publish
* timer_publish
* excel_export
* excel_import

### run:
```
uvicorn app.services.tasks_scheduler.async_tasks.app:app --port 7001 --log-level info
```
