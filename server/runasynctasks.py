import asyncio

import uvicorn
import uvloop

from app.services.tasks_scheduler.async_tasks.app import app


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7001)
