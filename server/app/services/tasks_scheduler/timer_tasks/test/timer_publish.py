import asyncio

import asyncpg
from app.timer_publish import timer_publish_task

from actor_libs.database.async_db import db


project_config = {}


async def timer_publish_t():
    _pool = await asyncpg.create_pool(
        host=project_config.get('POSTGRES_HOST', 'localhost'),
        port=project_config.get('POSTGRES_PORT', 5432),
        user=project_config.get('POSTGRES_USER', 'root'),
        password=project_config.get('POSTGRES_PASSWORD', 'public'),
        database=project_config.get('POSTGRES_DATABASE', 'actorcloud'),
        min_size=5, max_size=10
    )
    db.pool = _pool
    result = await timer_publish_task()
    print(result)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(timer_publish_t())
