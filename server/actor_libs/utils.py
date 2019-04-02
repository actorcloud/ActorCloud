import glob
import os
import subprocess
import uuid
from typing import AnyStr, Set, Tuple, Dict

import arrow
from flask import request

from actor_libs.errors import ParameterInvalid


def generate_uuid() -> str:
    """
    Generate 32 bit uuid
    """

    uid = str(uuid.uuid1()).replace('-', '')
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uid)).replace('-', '')
    return uid


def get_cwd() -> AnyStr:
    """
    Get the project directory
    """
    try:
        a = os.stat(os.environ['PWD'])
        b = os.stat(os.getcwd())
        if a.st_ino == b.st_ino and a.st_dev == b.st_dev:
            cwd = os.environ['PWD']
        else:
            cwd = os.getcwd()
    except Exception:
        cwd = os.getcwd()
    return cwd


def get_services_path() -> dict:
    """
    Get the services name and path
    :return: dict {service_name:service_path}
    """

    services_dict = {}
    backend_path = get_cwd()
    views_paths_re = os.path.join(backend_path, 'app/*/*/views/')
    views_paths = glob.glob(views_paths_re)
    for views_path in views_paths:
        service_path = os.path.abspath(os.path.join(views_path, os.pardir))
        service_name = os.path.basename(service_path)
        services_dict[service_name] = service_path
    return services_dict


def execute_shell_command(command: AnyStr, output: bool = False, cwd=None) -> AnyStr:
    """ Call subprocess execute command"""

    if not cwd:
        cwd = get_cwd()
    execute_info = ''
    if output:
        try:
            command_list = command.split()
            execute_info = subprocess.check_output(
                command_list, cwd=cwd
            )
        except Exception as e:
            raise RuntimeError(e)
    else:
        try:
            subprocess.call(command, shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output)
    return execute_info


def get_default_device_count() -> AnyStr:
    """
    Get the number of devices that tenant can manage
    """

    from actor_libs.project_config import get_project_config

    project_config = get_project_config()
    default_devices_limit = project_config['DEFAULT_DEVICES_LIMIT']
    return str(default_devices_limit)


def get_delete_ids() -> Set[int]:
    """
    Get a list of delete id with flask request context
    """

    try:
        delete_ids = set([int(delete_id) for delete_id in request.args.get('ids').split(',')])
    except Exception:
        raise ParameterInvalid(field='ids')
    return delete_ids


def validate_time_period_query(limit_days: int = 7) -> Tuple[str, str]:
    start_time = request.args.get('start_time', type=str)
    end_time = request.args.get('end_time', type=str)
    if not (start_time and end_time):
        raise ParameterInvalid('start_time or end_time')

    try:
        start_time = arrow.get(start_time)
    except Exception:
        raise ParameterInvalid('start_time')
    try:
        end_time = arrow.get(end_time)
    except Exception:
        raise ParameterInvalid('end_time')

    if end_time.day - start_time.day > limit_days:
        start_time = end_time.shift(days=-limit_days)

    time_format = 'YYYY-MM-DD HH:mm:ss'
    start_time = start_time.format(time_format)
    end_time = end_time.format(time_format)

    return start_time, end_time


def get_charts_config(time_unit: str = None, end_time: str = None,
                      start_time: str = None) -> dict:
    """
    Generate chart info(start time and x-axis data)
    :param start_time: start time
    :param end_time: end time
    :param time_unit: time unit
    """

    if end_time:
        try:
            end_time = arrow.get(end_time)
        except Exception:
            raise TypeError('end_time')
    else:
        end_time = arrow.now()

    if time_unit == 'hour':
        if start_time:
            start_time = arrow.get(start_time)
        else:
            start_time = end_time.shift(days=-1)
        x_data = [day.format('HH:00')
                  for day in arrow.Arrow.range('hour', start_time, end_time)]
    elif time_unit == 'day':
        if start_time:
            start_time = arrow.get(start_time)
        else:
            start_time = end_time.shift(months=-1)
        x_data = [day.format('YYYY-MM-DD')
                  for day in arrow.Arrow.range('day', start_time, end_time)]
    elif time_unit == 'month':
        if start_time:
            start_time = arrow.get(start_time)
        else:
            start_time = end_time.shift(years=-1)
        x_data = [month.format('YYYY-MM')
                  for month in arrow.Arrow.range('month', start_time, end_time)]
    elif time_unit == 'year':
        if start_time:
            start_time = arrow.get(start_time)
        else:
            start_time = end_time.shift(years=-5)
        x_data = [year.format('YYYY')
                  for year in arrow.Arrow.range('year', start_time, end_time)]
    else:
        raise AttributeError('time_unit')
    charts_config = {'start_time': start_time.naive, 'x_data': x_data[1:-1]}
    return charts_config


def check_interval_time(interval_time: Dict):
    """
    Check if interval time is valid
    interval_time: {'weekday': 0, 'hour': 0, 'minute': 1}
    """

    check_status = False
    interval_types = interval_time.keys()
    for interval_type, interval_value in interval_time.items():
        if interval_type == 'minute' and interval_value in range(0, 60):
            check_status = True
        elif all([interval_type == 'hour',
                  interval_value in range(0, 24),
                  'minute' in interval_types]):
            check_status = True
        elif all([interval_type == 'weekday',
                  interval_value in range(0, 7),
                  'hour' in interval_types,
                  'minute' in interval_types]):
            check_status = True
        else:
            check_status = False
        if not check_status:
            break
    return check_status
