import asyncio

import uvloop
from mode import Worker

from app.services.tasks_scheduler.timer_tasks.app.base import app


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


if __name__ == '__main__':
    Worker(app, loglevel="info", loop=loop).execute_from_commandline()


