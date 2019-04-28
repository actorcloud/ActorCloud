from typing import Dict

import json
from .base import handle_base_response, ActorResponse


__all__ = ['handle_emqx_publish_response', 'handle_emqx_rule_response']


def handle_emqx_publish_response(response: ActorResponse) -> Dict:
    """
    Handle emqx publish response
    """

    handled_response = handle_base_response(response)
    if handled_response.get('status') == 4:
        return handled_response

    try:
        response_dict = json.loads(response.responseContent)
    except Exception:
        response_dict = {'message': response.responseContent}

    handled_response['taskID'] = response.taskID
    code = response_dict.get('code')
    if code != 0 and response_dict.get('message'):
        # Error from emqx
        handled_response['status'] = 4
        handled_response['error'] = response_dict['message']
    elif code != 0 and not response_dict.get('message'):
        # Other unknown situation
        handled_response['status'] = 4
        handled_response['error'] = response.responseContent
    return handled_response


def handle_emqx_rule_response(response: ActorResponse) -> Dict:
    """ Handle emqx message rule response """

    handled_response = handle_base_response(response)
    if handled_response.get('status') == 4:
        return handled_response
    handled_response['message'] = response.responseContent
    return handled_response
