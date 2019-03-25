from .db_base import db_operate
from .table_init import (
    init_system_info, init_admin_account, init_dict_code
)


__all__ = [
    'db_operate', 'init_system_info', 'init_admin_account', 'init_dict_code'
]
