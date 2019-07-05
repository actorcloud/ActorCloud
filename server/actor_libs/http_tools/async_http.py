import logging
from asyncio import TimeoutError, gather
from logging import Logger
from typing import List, AnyStr

from aiohttp import BasicAuth, ClientSession
from aiohttp.client_exceptions import ClientConnectionError

from .responses import ActorResponse


logger = logging.getLogger('AsyncHttp')


class AsyncHttp:
    def __init__(self, auth: BasicAuth = None):
        self.auth = auth
        self.session = self.request_session()

    def request_session(self) -> ClientSession:
        headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }
        session = ClientSession(headers=headers, auth=self.auth)
        return session

    async def _fetch(self, method_session, url: AnyStr, **kwargs):
        request_json = kwargs.get('json')
        try:
            logger.debug(f"{url} -> kwargs:{kwargs}")
            async with method_session(url, timeout=3, **kwargs) as response:
                response_content = await response.read()
                response_code = response.status
            logger.debug(f"{url} -> response:{response_content}")
        except ClientConnectionError:
            response_content = 'client connection error!'
            response_code = 500
            logger.error(f"{url} -> {response_content}", exc_info=True)
        except TimeoutError:
            response_content = f'timeout error!'
            response_code = 500
            logger.error(f"{url} -> {response_content}", exc_info=True)
        except Exception as e:
            response_content = f'{e}'
            response_code = 500
            logger.error(f"{url} -> {response_content}", exc_info=True)
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

    async def get_url(self, url: AnyStr, **kwargs) -> ActorResponse:
        response = await self._fetch(self.session.get, url, **kwargs)
        return response

    async def _get_urls(self, urls: List, **kwargs) -> list:
        request_tasks = [
            self._fetch(self.session.get, url, **kwargs)
            for url in urls
        ]
        responses = await gather(
            *request_tasks, return_exceptions=True
        )
        return responses

    async def post_url(self, url: AnyStr, **kwargs) -> ActorResponse:
        response = await self._fetch(self.session.post, url, **kwargs)
        return response

    async def post_url_args(self, url: str, requests_json: list, **kwargs) -> str:
        request_tasks = [
            self._fetch(self.session.post, url=url, json=request_json, **kwargs)
            for request_json in requests_json
        ]
        responses = await gather(
            *request_tasks, return_exceptions=True
        )
        return responses

    async def post_urls(self, urls: List, **kwargs) -> List:
        request_tasks = [
            self._fetch(self.session.post, url, **kwargs)
            for url in urls
        ]
        responses = await gather(
            *request_tasks, return_exceptions=True
        )
        return responses

    async def _put_url(self, url: AnyStr, **kwargs) -> ActorResponse:
        response = await self._fetch(self.session.put, url, **kwargs)
        return response

    async def _put_urls(self, urls: List, **kwargs) -> List:
        request_tasks = [
            self._fetch(self.session.put, url, **kwargs)
            for url in urls
        ]
        responses = await gather(
            *request_tasks, return_exceptions=True
        )
        return responses

    async def _delete_url(self, url: AnyStr, **kwargs) -> ActorResponse:
        response = await self._fetch(self.session.delete, url, **kwargs)
        return response

    async def _delete_urls(self, urls: List, **kwargs) -> List:
        request_tasks = [
            self._fetch(self.session.delete, url, **kwargs)
            for url in urls
        ]
        responses = await gather(
            *request_tasks, return_exceptions=True
        )
        return responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
