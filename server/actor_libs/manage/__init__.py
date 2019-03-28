from .data_init import (
    db_operate, init_system_info, init_admin_account, init_dict_code
)

__all__ = ['ProjectManage']


class ProjectManage:

    @staticmethod
    def project_deploy():
        db_operate(execute_type='deploy')
        init_system_info()
        init_admin_account()
        init_dict_code()

    @staticmethod
    def project_upgrade():
        db_operate(execute_type='upgrade')
        init_system_info()
        init_dict_code()

