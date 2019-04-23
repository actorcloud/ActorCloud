import ujson
from base64 import b64encode


__all__ = ['lwm2m_publish_json']


def lwm2m_publish_json(request_dict):
    """ Building client publish json of lwm2m protocol """

    # build publish payload
    publish_payload = _build_publish_payload(request_dict)
    publish_json = {
        'topic': request_dict['prefixTopic'] + '/dn',
        'payload': ujson.dumps(publish_payload)
    }
    return publish_json


def _build_publish_payload(request_dict):
    control_type = request_dict.get('controlType')
    payload = request_dict['payload']
    path = request_dict['topic']

    if control_type == 1:
        # read
        data = {"path": path}
    elif control_type == 2:
        # write
        if path == '/19/1/0':
            value_type = 'Opaque'
        else:
            # how to get value type of standard lwm2m protocol? todo
            value_type = ''
        data = {
            "path": path,
            'type': value_type,
            'value': b64encode(payload['value'].encode()).decode()
        }
    elif control_type == 3:
        # execute
        data = {
            "path": path,
            'args': payload['value']
        }
    else:
        data = {}
    publish_payload = {
        'reqID': request_dict['taskID'],
        'msgType': payload['msgType'],
        'data': data
    }
    return publish_payload
