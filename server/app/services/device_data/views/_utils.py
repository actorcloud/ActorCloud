import arrow
from flask import request
from sqlalchemy import text

from actor_libs.errors import ParameterInvalid
from app.models import DeviceEvent


__all__ = ['add_time_filter']


def add_time_filter(events_query):
    time_type = request.args.get('timeType', type=str)
    if time_type == 'realtime':
        events_query = events_query \
            .filter(DeviceEvent.msgTime >= text("NOW() - INTERVAL '1 DAYS'"))
    elif time_type == 'history':
        _validate_time_range()
    else:
        raise ParameterInvalid(field='timeType')

    return events_query


def _validate_time_range(limit_days: int = 7) -> None:
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
