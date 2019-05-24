import asyncio

import uvloop
from mode import Worker

from actor_libs.tasks.timer import App
from .api_count import api_count_aggr
from .device_count import device_count_aggr
from .device_events import device_events_aggr
from .emqx_bills import emqx_bills_aggr
from actor_libs.database.async_db import db
from .config import project_config


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


app = App(node_id='timer_task')


__all__ = ['project_config', 'postgres', 'faust_app', 'task_process']


@app.crontab(cron_format='2 * * * *', timezone=project_config['TIMEZONE'])
async def device_count_task():
    """ Aggregate device count at second minute of every hour """

    await device_count_aggr()


@app.crontab(cron_format='3 * * * *', timezone=project_config['TIMEZONE'])
async def api_count_task():
    """ Aggregate api count at third minute of every hour """

    await api_count_aggr()


@app.crontab(cron_format='5 * * * *', timezone=project_config['TIMEZONE'])
async def emqx_bills_task():
    """  Aggregate emqx bills at five minute of every hour """

    await emqx_bills_aggr()


@app.crontab(cron_format='7 * * * *', timezone=project_config['TIMEZONE'])
async def device_event_tasks():
    """  Aggregate device events at seven minute of every hour """

    await device_events_aggr()


if __name__ == '__main__':
    Worker(app, loglevel="info", loop=loop).execute_from_commandline()
