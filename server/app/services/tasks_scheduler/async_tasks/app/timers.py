from . import faust_app
from ._lib.timer_parse import get_due_tasks
from .tasks import timer_publish_task


@faust_app.timer(60)
async def _send_timer_publish():
    due_tasks_id = await get_due_tasks()
    if due_tasks_id:
        await timer_publish_task.delay(due_tasks_id=due_tasks_id)
