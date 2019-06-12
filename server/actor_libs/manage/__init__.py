from .data_init import (
    db_operate, convert_timescaledb, init_services, init_resources,
    init_default_roles, update_default_roles, init_admin_account,
    init_dict_code, init_system_info, init_lwm2m_info, create_triggers
)
from .supervisord import supervisord_config


__all__ = ['ProjectManage']


class ProjectManage:

    @staticmethod
    def project_deploy():
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

    @staticmethod
    def project_upgrade():
        db_operate(execute_type='upgrade')
        init_services()
        init_resources()
        update_default_roles()
        init_dict_code()
        init_system_info()
        init_lwm2m_info()
        supervisord_config()
