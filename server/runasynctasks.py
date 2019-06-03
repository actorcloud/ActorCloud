import asyncio

import uvicorn
import uvloop

from app.services.tasks_scheduler.async_tasks.app import app
from config import BaseConfig


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


if __name__ == '__main__':
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
