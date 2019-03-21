from typing import AnyStr

import requests
from flask import current_app
from requests.exceptions import Timeout, ConnectionError

from .responses import ActorResponse


class SyncHttp:

    def __init__(self, auth=None):
        self.auth = auth

    def _fetch(self, method, url: AnyStr, **kwargs):
        if kwargs.get('headers'):
            headers = kwargs.pop('headers')
        else:
            headers = {
                'content-type': 'application/json',
                'cache-control': 'no-cache'
            }

        try:
            response = requests.request(
                method, url=url, auth=self.auth,
                headers=headers, timeout=3, **kwargs
            )
            current_app.logger.debug(f'Response status code is {response.status_code}'
                                     f' and content is {response.content}')
            response_content = response.content
            response_code = response.status_code
        except Timeout:
            # logs e todo
            response_content = f'client connection error!'
            response_code = 500
        except ConnectionError:
            # logs e todo
            response_content = f'client connection error!'
            response_code = 500
        except Exception as e:
            response_content = f'{e}'
            response_code = 500
        request_json = kwargs.get('json')
        if request_json:
            task_id = request_json.get('taskID') or request_json.get('task_id')
        else:
            task_id = None
        if isinstance(response_content, bytes):
            response_content = response_content.decode('utf-8')
        actor_response = ActorResponse(
            taskID=task_id, taskStatus=1,
            responseCode=response_code, responseContent=response_content
        )
        return actor_response

    def get(self, url, **kwargs):
        response = self._fetch(
            'GET', url=url, **kwargs
        )
        return response

    def post(self, url, **kwargs):
        response = self._fetch(
            'POST', url=url, **kwargs
        )
        return response

    def put(self, url, **kwargs):
        response = self._fetch(
            'PUT', url=url, **kwargs
        )
        return response

    def delete(self, url, **kwargs):
        response = self._fetch(
            'DELETE', url=url, **kwargs
        )
        return response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
