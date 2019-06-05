import arrow
from flask import request

from actor_libs.errors import ParameterInvalid


__all__ = ['validate_time_range']


def validate_time_range(limit_days: int = 7) -> None:
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
        raise ParameterInvalid('Time range is greater than 7 days')
