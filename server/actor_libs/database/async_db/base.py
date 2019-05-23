import logging
from typing import List, Deque, Tuple, Any


__all__ = ['AsyncPostgres']


logger = logging.getLogger(__name__)


class AsyncPostgres:
    _instance = None
    pool = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AsyncPostgres, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    async def open(self, pool) -> None:
        self.pool = pool

    async def close(self) -> None:
        if not self.pool:
            return
        await self.pool.close()

    async def execute(self, sql: str, *args) -> bool:
        """
        insert/update/delete SQL
        """

        async with self.pool.acquire() as conn:
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

        async with self.pool.acquire() as conn:
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

        async with self.pool.acquire() as conn:
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
