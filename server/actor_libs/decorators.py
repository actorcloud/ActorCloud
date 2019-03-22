from functools import partial, wraps
from time import time

from flask import request

from .errors import APIException, DataNotFound, ResourceLimited


def ip_limit(func=None, allow_list=None):
    """ Limit the ip which not in allow list and EMQX node """
    from itertools import chain

    if func is None:
        return partial(ip_limit, allow_list=allow_list)

    @wraps(func)
    def decorated(*args, **kwargs):
        from flask import current_app

        emq_nodes = current_app.config.get('EMQ_NODES')
        nodes = [node.get('ip') for node in emq_nodes]
        if not isinstance(emq_nodes, list):
            raise Exception('The EMQ_NODES not set a ip list')
        if allow_list and not isinstance(allow_list, list):
            raise Exception('The ip filter object not set a filter list')

        allow_ip_list = (list(chain(nodes, allow_list)) if allow_list else nodes)
        ip = request.headers.get('X-Real-Ip') or request.remote_addr
        if ip not in allow_ip_list:
            raise DataNotFound(field='url')
        return func(*args, **kwargs)

    return decorated


def limit_upload_file(func=None, size=104857600):
    """ Limit upload file size (default 100MB) """
    if func is None:
        return partial(limit_upload_file, size=size)

    @wraps(func)
    def decorated(*args, **kwargs):
        request_file = request.files.get('file')
        if not request_file:
            raise DataNotFound(field='file')
        try:
            request_size = int(request.content_length)
        except Exception:
            raise APIException()
        if request_size > size:
            raise ResourceLimited(field='file')
        return func(*args, **kwargs)

    return decorated


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(func.__name__, end_time - start_time)
        return result

    return wrapper
