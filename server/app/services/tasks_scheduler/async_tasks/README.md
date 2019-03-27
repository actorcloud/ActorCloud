# actorcloud async tasks

* device_publish
* group_publish
* timer_publish
* excel_export
* excel_import

### run:
```
faust -A app.services.tasks_scheduler.async_tasks.app.faust_app worker -l info
```
