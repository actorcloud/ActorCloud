import asyncpg

from actor_libs.database.async_db import db
from actor_libs.tasks.timer import App
from .api_count import api_count_task
from .config import project_config
from .device_count import device_count_task
from .device_events import device_events_aggr_task
from .emqx_bills import emqx_bills_aggr_task
from .timer_publish import timer_publish_task


__all__ = ['app']


app = App(node_id='timer_task')


@app.on_event('startup')
async def open_database_connection_poll():
    _pool = await asyncpg.create_pool(
        host=project_config.get('POSTGRES_HOST', 'localhost'),
        port=project_config.get('POSTGRES_PORT', 5432),
        user=project_config.get('POSTGRES_USER', 'root'),
        password=project_config.get('POSTGRES_PASSWORD', 'public'),
        database=project_config.get('POSTGRES_DATABASE', 'actorcloud'),
        min_size=5, max_size=10
    )
    await db.open(_pool)


@app.on_event('shutdown')
async def close_database_connection_poll():
    await db.close()


@app.crontab(cron_format='2 * * * *', timezone=project_config['TIMEZONE'])
async def device_count():
    """ Aggregate device count at second minute of every hour """
    task_result = await device_count_task()
    return task_result


@app.crontab(cron_format='3 * * * *', timezone=project_config['TIMEZONE'])
async def api_count():
    """ Aggregate api count at third minute of every hour """
    task_result = await api_count_task()
    return task_result


@app.crontab(cron_format='5 * * * *', timezone=project_config['TIMEZONE'])
async def emqx_bills_aggr():
    """  Aggregate emqx bills at five minute of every hour """
    task_result = await emqx_bills_aggr_task()
    return task_result


@app.crontab(cron_format='7 * * * *', timezone=project_config['TIMEZONE'])
async def device_event_aggr():
    """  Aggregate device events at seven minute of every hour """
    task_result = await device_events_aggr_task()
    return task_result


@app.timer(interval=10)
async def timer_publish():
    """  Check for timer tasks every 59 seconds  """
    await timer_publish_task()
