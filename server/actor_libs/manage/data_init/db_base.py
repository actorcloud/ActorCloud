import os
from typing import AnyStr

from flask import current_app
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from actor_libs.database.orm import db
from actor_libs.utils import execute_shell_command

__all__ = ['db_operate']


def db_operate(execute_type: AnyStr) -> None:
    """ Operate database: migrate or deploy """

    _check_db_table(execute_type)
    project_backend = current_app.config['BACKEND_PATH']
    if execute_type == 'upgrade':
        truncate_db_version = '''
            TRUNCATE TABLE alembic_version RESTART IDENTITY;
        '''
        try:
            db.engine.execute(
                text(truncate_db_version).execution_options(autocommit=True)
            )
        except ProgrammingError:
            raise RuntimeError('Please specify deploy or upgrade! ')
    elif execute_type == 'deploy':
        try:
            db.create_all(app=current_app)
            print('database init')
        except OperationalError as e:
            raise RuntimeError(e)
    else:
        pass

    orm_dir = os.path.join(project_backend, 'migrations/orm')
    execute_shell_command(command=f"rm -rf {orm_dir}")
    execute_shell_command(command=f"flask db init --directory='{orm_dir}'")
    execute_shell_command(command=f"flask db migrate --directory='{orm_dir}'")
    execute_shell_command(command=f"flask db upgrade --directory='{orm_dir}'")
    info = f"database {execute_type} successfully!"
    print(info)


def _check_db_table(execute_type: AnyStr):
    table_check_sql = """
    SELECT to_regclass('public.system_info');
    """
    is_exist = db.engine.execute(
        text(table_check_sql).execution_options(autocommit=True)
    ).first()
    if is_exist[0] and execute_type == 'deploy':
        raise RuntimeError('DeployError: database table already exists!')
    if not is_exist[0] and execute_type == 'migrate':
        raise RuntimeError('MigrateError: database table not exists!')
