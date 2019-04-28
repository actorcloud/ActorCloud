import json

__all__ = ['base_publish_json']


def base_publish_json(request_dict):
    """
    Building client publish json of base protocol
    base protocol: MQTT(1), CoAP(2), WebSocket(6)
    """

    # build publish payload
    publish_payload = {
        'data_type': 'request',
        'task_id': request_dict['taskID'],
        'data': request_dict['payload']
    }
    if request_dict.get('streamID'):
        publish_payload['stream_id'] = request_dict['streamID']
    publish_json = {
        'topic': request_dict['prefixTopic'] + request_dict['topic'],
        'payload': json.dumps(publish_payload)
    }
    return publish_json
