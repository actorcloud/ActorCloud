import json
from base64 import b64encode


__all__ = ['lwm2m_publish_json']


def lwm2m_publish_json(request_dict):
    """ Building client publish json of lwm2m protocol """

    payload = request_dict['payload']
    msg_type = payload.pop('msgType')
    if payload['path'] == '/19/1/0':
        payload['value'] = json.dumps(payload['value'])
    if msg_type == 'write':
        # lwm2m write msg type require base64 encode
        payload['value'] = b64encode(payload['value'].encode()).decode()
    publish_payload = {
        'reqID': request_dict['taskID'],
        'msgType': msg_type,
        'data': payload
    }
    if request_dict.get('streamID'):
        publish_payload['stream_id'] = request_dict['streamID']
    publish_json = {
        'qos': 1,
        'topic': request_dict['prefixTopic'] + 'dn',
        'payload': json.dumps(publish_payload)
    }
    return publish_json
