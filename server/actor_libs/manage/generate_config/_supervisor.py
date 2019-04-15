import getpass
import os
from glob import glob
from typing import AnyStr, List, Tuple, Dict

from flask import current_app

from ._gunicorn import gunicorn_config
from actor_libs.utils import execute_shell_command
from .jinja_templates import insert_jinja_template


__all__ = ['supervisor_config']


def supervisor_config(run_services: List = None) -> None:
    """
    run_services: ['backend', 'streams_engine', 'tasks_scheduler']
    """

    project_config = current_app.config
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
        project_path, 'deploy/production/supervisor/actorcloud.conf'
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

    project_path = project_config['PROJECT_PATH']
    log_level = project_config['LOG_LEVEL']
    task_names = _get_task_scheduler_names(project_path)

    services_config = []
    group_names = []
    for task_name in task_names:
        project_name = f"tasks_scheduler-{task_name}"
        worker_path = os.path.join(project_path, f'actor_data/{project_name}/worker_1')
        if not os.path.isdir(worker_path):
            os.makedirs(worker_path)
        base_command = f"{venv_path}/bin/faust --datadir='{worker_path}' -A " \
            f"app.services.tasks_scheduler.{task_name}.app.faust_app" \
            f" worker -l {log_level}"
        if task_name == 'async_tasks':
            run_command = base_command
        else:
            run_command = base_command + ' --without-web'

        server_config = {
            'name': project_name,
            'command': run_command,
            'directory': project_config['PROJECT_PATH'],
            'log': f"{project_config['LOG_PATH']}/tasks_scheduler.log",
            'user': project_config['USERNAME']
        }
        services_config.append(server_config)
        group_names.append(project_name)
    return services_config, group_names


def _get_task_scheduler_names(project_path: AnyStr) -> List[AnyStr]:
    task_names = []
    tasks_scheduler_path = os.path.join(
        project_path, 'app/services/tasks_scheduler/*/'
    )
    task_dir_list = glob(tasks_scheduler_path)
    for task_dir in task_dir_list:
        task_name = os.path.basename(os.path.dirname(task_dir))
        if not os.path.isdir(task_dir):
            continue
        if task_name.endswith('tasks') or task_name.endswith('aggr'):
            task_names.append(task_name)
    return task_names


def _get_virtualenv_path() -> AnyStr:
    command = 'pipenv --venv'
    execute_info = execute_shell_command(command=command, output=True).decode('utf-8')
    venv_path = execute_info.replace("\n", "")
    if not os.path.isdir(venv_path):
        raise RuntimeError('Get virtualenv path error!')
    return venv_path
