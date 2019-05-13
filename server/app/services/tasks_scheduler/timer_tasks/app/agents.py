import arrow
from faust import Stream

from actor_libs.tasks.model import TaskInfo
from actor_libs.tasks.task import handle_task_result
from . import faust_app, task_process, postgres, project_config


@faust_app.agent(faust_app.tasks_channel)
async def process_task(tasks: Stream[TaskInfo]) -> None:
    tasks.add_processor(task_process)
    async for actor_task in tasks:
        date_now = arrow.now(tz=project_config['TIMEZONE']).naive
        await handle_task_result(
            postgres=postgres,
            actor_task=actor_task,
            date_now=date_now
        )
