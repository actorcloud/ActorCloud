from .base import AsyncPostgres


__all__ = ['db']

db = AsyncPostgres()
