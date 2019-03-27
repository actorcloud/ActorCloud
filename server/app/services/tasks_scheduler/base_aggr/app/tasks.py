from actor_libs.tasks.base import task
from actor_libs.types import TaskResult
from . import faust_app
from .api_count.api_count_aggr import api_count_aggr
from .device_count.device_count_aggr import device_count_aggr
from .emqx_bills.emqx_bills_aggr import emqx_bills_aggr


__all__ = ['device_aggr_task', 'api_aggr_task', 'emqx_bills_aggr_task']


@task(app=faust_app, task_name='device_aggr_task')
async def device_aggr_task() -> TaskResult:
    """ Aggregate device count at first minute of every hour """

    result = await device_count_aggr()
    return result


@task(app=faust_app, task_name='api_aggr_task')
async def api_aggr_task() -> TaskResult:
    """  Aggregate api count at second minute of every hour """

    result = await api_count_aggr()
    return result


@task(app=faust_app, task_name='emqx_bills_aggr_task')
async def emqx_bills_aggr_task() -> TaskResult:
    """ Aggregate emqx bills at third minute of every hour """

    result = await emqx_bills_aggr()
    return result
