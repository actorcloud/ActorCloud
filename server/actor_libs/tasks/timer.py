import asyncio
from functools import wraps, partial

from mode import Service
from mode.timers import timer_intervals
from mode.utils.objects import qualname

from ._utils import secs_for_next


class App(Service):
    channel = None
    _timer_tasks = []

    def __init__(self, node_id, *, loop=None):
        self.node_id = node_id
        super().__init__(loop=loop)

    def timer(self, func=None, interval=60):
        if func is None:
            return partial(self.timer, interval=interval)

        timer_name = qualname(func)

        @wraps(func)
        async def decorated(*args, **kwargs):
            await self.sleep(interval)
            for sleep_time in timer_intervals(
                    interval, name=timer_name,
                    max_drift_correction=0.1):
                if self.should_stop:
                    break
                await func(*args, **kwargs)
                await self.sleep(sleep_time)
                if self.should_stop:
                    break
        return self._timer_tasks.append(decorated)

    def crontab(self, func=None, cron_format: str = None, timezone=None):
        if func is None:
            return partial(self.crontab, cron_format=cron_format, timezone=timezone)

        @wraps(func)
        async def decorated(*args, **kwargs):
            while not self.should_stop:
                next_time = secs_for_next(cron_format, timezone)
                await asyncio.sleep(next_time)
                await func(*args, **kwargs)

        return self._timer_tasks.append(decorated)

    async def send(self, send_value):
        ...

    def _channel(self):
        ...

    def _agent(self):
        ...

    async def on_started(self):
        for task in self._timer_tasks:
            self.add_future(task())
