from .data_init import (
    db_operate, convert_timescaledb, init_services, init_resources,
    init_default_roles, update_default_roles, init_admin_account,
    init_dict_code, init_system_info, init_lwm2m_info, create_triggers
)
from .supervisord import supervisord_config


class Manage:
    def deploy(self):
        db_operate(execute_type='deploy')
        convert_timescaledb()
        create_triggers()
        init_services()
        init_resources()
        init_default_roles()
        init_admin_account()
        init_dict_code()
        init_system_info()
        init_lwm2m_info()
        supervisord_config()
        self.extend_deploy()

    def upgrade(self):
        db_operate(execute_type='upgrade')
        init_services()
        init_resources()
        update_default_roles()
        init_dict_code()
        init_system_info()
        init_lwm2m_info()
        supervisord_config()
        self.extend_upgrade()

    def extend_deploy(self):
        ...

    def extend_upgrade(self):
        ...
