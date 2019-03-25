from .data_init import (
    db_operate, init_system_info, init_admin_account
)


__all__ = ['project_deploy', 'project_upgrade']


def project_deploy():
    db_operate(execute_type='deploy')
    init_system_info()
    init_admin_account()


def project_upgrade():
    db_operate(execute_type='upgrade')
    init_system_info()
