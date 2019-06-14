import click
from config import BaseConfig


@click.group()
def actorcloud_run():
    pass


@actorcloud_run.command()
def backend():
    from manage import app

    base_config = BaseConfig().config
    _port = int(base_config['BACKEND_NODE'].split(':')[-1])
    log_level = base_config['LOG_LEVEL']
    if log_level == 'debug':
        debug = True
    else:
        debug = False
    app.run(host='0.0.0.0', port=_port, debug=debug)


@actorcloud_run.command()
def async_tasks():
    import uvicorn

    from app.services.tasks_scheduler.async_tasks.app import app

    base_config = BaseConfig().config
    _port = int(base_config['ASYNC_TASKS_NODE'].split(':')[-1])
    log_level = base_config['LOG_LEVEL']
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=_port,
        loop='uvloop',
        log_level=log_level
    )


@actorcloud_run.command()
def timer_tasks():
    import asyncio

    import uvloop
    from mode import Worker

    from app.services.tasks_scheduler.timer_tasks.app.base import app

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    base_config = BaseConfig().config
    log_level = base_config['LOG_LEVEL']
    worker = Worker(app, loglevel=log_level, loop=loop)
    worker.execute_from_commandline()


if __name__ == '__main__':
    actorcloud_run()
