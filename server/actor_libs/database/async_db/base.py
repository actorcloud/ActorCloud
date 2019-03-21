# coding: utf-8

import logging
from typing import List, Deque, Tuple, Any

import asyncpg


__all__ = ['AsyncPostgres']

logger = logging.getLogger(__name__)


class AsyncPostgres:
    def __init__(self, host='localhost', port='5432', user='root', password='public',
                 database='platform', min_size=10, max_size=20) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.min_size = min_size
        self.max_size = max_size
        self._pool = None

    async def pool(self) -> Any:
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=self.min_size,
                max_size=self.max_size,
            )
        return self._pool

    async def close(self) -> None:
        if not self._pool:
            return
        await self._pool.close()

    async def execute(self, sql: str, *args) -> bool:
        """
        insert/update/delete SQL
        """
        pool = await self.pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                query_sql = sql.replace("'NULL'", "NULL")
                try:
                    await conn.execute(query_sql, *args)
                    logger.info(query_sql)
                    execute_status = True
                except Exception as e:
                    logger.error(e)
                    logger.error(query_sql)
                    execute_status = False
        return execute_status

    async def fetch(self, sql: str, fetch_type: str) -> Any:
        """
        :param sql: sql statement
        :param fetch_type: row or many or val
        """
        pool = await self.pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    if fetch_type == 'row':
                        result = await conn.fetchrow(sql)
                    elif fetch_type == 'many':
                        result = await conn.fetch(sql)
                    elif fetch_type == 'val':
                        result = await conn.fetchval(sql)
                    return result
                except Exception as e:
                    logger.error(sql)
                    logger.error(e)

    async def fetch_many(self, sql: str) -> list:
        return await self.fetch(sql, 'many')

    async def fetch_row(self, sql: str) -> Any:
        return await self.fetch(sql, 'row')

    async def fetch_val(self, sql: str) -> Any:
        return await self.fetch(sql, 'val')

    async def insert_records(self, table_name: str, columns: List[str],
                             deque: Deque) -> None:
        """
        Insert records with copy
        """
        deque_length = len(deque)
        if deque_length != 0:
            # 5000 max
            deque_length = deque_length if deque_length <= 5000 else 5000
            records = (
                deque.popleft() for _ in range(0, deque_length)
            )
            await self.copy_records_to_table(
                table_name, records=records, columns=columns
            )

    async def copy_records_to_table(self, table_name: str,
                                    records: [Tuple, List],
                                    columns: List[str]) -> bool:
        """ Copy a list of records to the specified table using binary COPY

        :param str table_name:
            The name of the table to copy data to.

        :param records:
            An iterable returning row tuples to copy into the table.

        :param list columns:
            An list of column names to copy.
        """
        pool = await self.pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.copy_records_to_table(
                        table_name, records=records, columns=columns
                    )
                    execute_status = True
                except Exception as error:
                    execute_status = False
                    logger.error(error)
        return execute_status
