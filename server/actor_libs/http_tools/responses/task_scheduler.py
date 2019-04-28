from typing import Dict

import json
from .base import handle_base_response


def handle_task_scheduler_response(response) -> Dict:
    """
    Handle task scheduler response,add taskID to response
    """

    handled_response = handle_base_response(response)
    try:
        response_dict = json.loads(response.responseContent)
    except Exception:
        response_dict = {}

    if handled_response.get('status') == 3 and response_dict.get('taskID'):
        handled_response['status'] = 3
        handled_response['taskID'] = response_dict['taskID']
    else:
        handled_response['status'] = 4
    return handled_response
