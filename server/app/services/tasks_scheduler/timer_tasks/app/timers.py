from . import faust_app, project_config
from .tasks import (
    device_aggr_task, api_aggr_task, emqx_bills_aggr_task, device_event_aggr_task
)


__all__ = ['device_aggr', 'api_aggr', 'emqx_bills_aggr']


@faust_app.crontab(cron_format='1 * * * *', timezone=project_config['TIMEZONE'])
async def device_aggr():
    """ Aggregate device count at first minute of every hour """
    task_info = await device_aggr_task.delay()
    return task_info


@faust_app.crontab(cron_format='2 * * * *', timezone=project_config['TIMEZONE'])
async def api_aggr():
    """ Aggregate api count at second minute of every hour """

    task_info = await api_aggr_task.delay()
    return task_info


@faust_app.crontab(cron_format='3 * * * *', timezone=project_config['TIMEZONE'])
async def emqx_bills_aggr():
    """  Aggregate emqx bills at third minute of every hour """

    task_info = await emqx_bills_aggr_task.delay()
    return task_info


@faust_app.crontab(cron_format='5 * * * *', timezone=project_config['TIMEZONE'])
async def device_event_aggr():
    """  Aggregate device events at five minute of every hour """

    task_info = await device_event_aggr_task.delay()
    return task_info
