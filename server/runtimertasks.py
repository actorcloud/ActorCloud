import asyncio

import uvloop
from mode import Worker

from app.services.tasks_scheduler.timer_tasks.app.base import app
from config import BaseConfig


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


if __name__ == '__main__':
    base_config = BaseConfig().config
    log_level = base_config['LOG_LEVEL']
    Worker(app, loglevel=log_level, loop=loop).execute_from_commandline()


