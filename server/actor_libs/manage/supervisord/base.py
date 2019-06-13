import getpass
import os
from typing import AnyStr, List, Tuple, Dict

from actor_libs.utils import execute_shell_command
from config import BaseConfig
from ._gunicorn import gunicorn_config
from ._templates import insert_jinja_template


__all__ = ['supervisord_config']


def supervisord_config(run_services: List = None) -> None:
    """
    run_services: ['backend', 'streams_engine', 'tasks_scheduler']
    """

    project_config = BaseConfig().config
    project_config['USERNAME'] = getpass.getuser()
    project_path = project_config['PROJECT_PATH']
    venv_path = _get_virtualenv_path()

    program_group = []
    services_config = []
    service_func_dict = {
        'backend': _backend_config,
        'tasks_scheduler': _tasks_scheduler_config
    }
    if not run_services:
        run_services = ['backend', 'tasks_scheduler']

    for run_service in run_services:
        service_func = service_func_dict[run_service]
        service_config, group_name = service_func(venv_path, project_config)
        program_group.extend(group_name)
        services_config.extend(service_config)
    supervisor_path = os.path.join(
        project_path, 'config/actorcloud_supervisord.conf'
    )
    jinja_config = {
        'group_programs': ','.join(program_group),
        'services': services_config
    }
    insert_jinja_template(
        project_path=project_path,
        out_path=supervisor_path,
        template_name='supervisor.jinja',
        jinja_config=jinja_config
    )
    info = "Generate supervisor config successfully!"
    print(info)


def _backend_config(venv_path, project_config) -> Tuple[List[Dict], List[str]]:
    """ flask supervisor config """

    project_name = 'backend'
    gunicorn_config_path = gunicorn_config()
    run_command = f"{venv_path}/bin/gunicorn -c {gunicorn_config_path} manage:app"
    server_config = {
        'name': project_name,
        'command': run_command,
        'directory': project_config['PROJECT_PATH'],
        'log': f"{project_config['LOG_PATH']}/{project_name}.log",
        'user': project_config['USERNAME']
    }
    servers_config = [server_config]
    group_names = [project_name]
    return servers_config, group_names


def _tasks_scheduler_config(venv_path, project_config) -> Tuple[List[Dict], List[str]]:
    """ tasks_scheduler supervisor config """

    async_tasks_config = {
        'name': 'async_tasks',
        'command': f"{venv_path}/bin/python run.py async-tasks",
        'directory': project_config['PROJECT_PATH'],
        'log': f"{project_config['LOG_PATH']}/async_tasks.log",
        'user': project_config['USERNAME']
    }
    timer_tasks_config = {
        'name': 'timer_tasks',
        'command': f"{venv_path}/bin/python run.py timer-tasks",
        'directory': project_config['PROJECT_PATH'],
        'log': f"{project_config['LOG_PATH']}/timer_tasks.log",
        'user': project_config['USERNAME']
    }
    services_config = [async_tasks_config, timer_tasks_config]
    group_names = ['async_tasks', 'timer_tasks']
    return services_config, group_names


def _get_virtualenv_path() -> AnyStr:
    command = 'pipenv --venv'
    execute_info = execute_shell_command(command=command, output=True).decode('utf-8')
    venv_path = execute_info.replace("\n", "")
    if not os.path.isdir(venv_path):
        raise RuntimeError('Get virtualenv path error!')
    return venv_path
