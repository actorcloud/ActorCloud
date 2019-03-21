from collections import namedtuple
from typing import Dict


__all__ = ['ActorResponse', 'handle_base_response']

ActorResponse = namedtuple(
    'ActorResponse',
    [
        'taskID',
        'taskStatus',
        'responseCode',
        'responseContent'
    ]
)


def handle_base_response(response) -> Dict:
    """
    Handle base response
    status: 1:waiting, 2:pending, 3:success, 4:fail
    """

    handled_response = {'status': 2}
    if response.responseCode == 200:
        handled_response['status'] = 3
    elif response.responseCode == 422:
        handled_response['status'] = 4
        handled_response['error'] = 'FORM_INVALID'
    elif response.responseCode == 401:
        # Auth failed
        handled_response['status'] = 4
        handled_response['error'] = 'AUTH_FAILED'
    elif response.responseCode == 500:
        # Timeout or emqx internal error
        handled_response['status'] = 4
        handled_response['error'] = response.responseContent
    else:
        # Other unknown error
        handled_response['status'] = 4
        handled_response['error'] = 'UNKNOWN_ERROR'
    return handled_response
