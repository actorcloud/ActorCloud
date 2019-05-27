import json

from flask import g
from marshmallow import pre_load, post_load
from sqlalchemy import func

from actor_libs.database.orm import db
from actor_libs.errors import FormInvalid
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqString, EmqInteger
)
from app.models import Device, Product, DictCode, Lwm2mItem


__all__ = [
    'PublishSchema'
]


class PublishSchema(BaseSchema):
    """
    Device publish schema
    prefixTopic: /protocol/tenantID/productID/deviceID/
    """

    deviceID = EmqString(required=True)
    topic = EmqString(required=True, len_max=1000)
    payload = EmqString(required=True, len_max=10000)
    streamID = EmqString(allow_none=True, len_max=500)
    deviceIntID = EmqInteger(load_only=True)  # client index id
    protocol = EmqString(load_only=True)  # device protocol: mqtt, coap, lwm2m, websocket, modbus
    cloudProtocol = EmqInteger(load_only=True)  # product cloud protocol: 1,2,3,4...
    prefixTopic = EmqString(load_only=True, len_max=1000)

    @pre_load
    def handle_data(self, data):
        device_uid = data.get('deviceID')
        if not isinstance(device_uid, str):
            raise FormInvalid(field='deviceID')
        client_info = db.session \
            .query(Device.id.label('deviceIntID'), Device.productID, Device.tenantID,
                   Device.deviceType, Product.gatewayProtocol,
                   DictCode.codeValue.label('cloudProtocol'),
                   func.lower(DictCode.enLabel).label('protocol')) \
            .join(Product, Product.productID == Device.productID) \
            .join(DictCode, DictCode.codeValue == Product.cloudProtocol) \
            .filter(Device.deviceID == device_uid, Device.tenantID == g.tenant_uid,
                    DictCode.code == 'cloudProtocol').to_dict()
        data.update(client_info)
        # modbus gateway
        if client_info.deviceType == 2 and client_info.gatewayProtocol == 7:
            data['prefixTopic'] = ''
        else:
            data['prefixTopic'] = (
                f"/{data['protocol']}/{data['tenantID']}"
                f"/{data['productID']}/{data['deviceID']}/"
            )
        return data

    @post_load
    def handle_protocol_publish(self, data):
        protocol = data['protocol']
        if protocol == 'lwm2m':
            data = _lwm2m_protocol(data)
        else:
            # handle '/' prefix topic
            topic = data['topic'] if data.get('topic') else 'inbox'
            data['topic'] = topic[1:] if topic.startswith('/') else topic
        return data


def _lwm2m_protocol(data):
    """ handle lwm2m protocol publish """

    try:
        load_payload = json.loads(data['payload'])
    except Exception:
        raise FormInvalid(field='payload')
    # build emqx lwm2m protocol require payload
    handled_payload = _validate_lwm2m_topic(data['topic'])
    if data['topic'] == '/19/1/0':
        handled_payload['msgType'] = 'write'
        handled_payload['value'] = load_payload
    else:
        msg_type = load_payload.get('msgType')
        if msg_type == 'read':
            # {'msgType': 'read', 'path': xx}
            handled_payload['msgType'] = 'read'
        elif msg_type == 'write' and load_payload.get('value'):
            # {'msgType': 'write', 'path': xx, 'value': xx, 'type': xx}
            handled_payload['msgType'] = 'write'
            handled_payload['value'] = load_payload['value']
        elif msg_type == 'execute':
            # {'msgType': 'execute', 'path': xx, 'args'}
            handled_payload['msgType'] = 'execute'
            if load_payload.get('args'):
                handled_payload['args'] = load_payload['args']
        else:
            raise FormInvalid(field='payload')
    data['payload'] = json.dumps(handled_payload)
    return data


def _validate_lwm2m_topic(topic: str) -> dict:
    handled_payload = {'path': topic}
    if topic == '/19/1/0':
        handled_payload['type'] = 'Opaque'
    else:
        product_item_info = [i for i in topic.split('/') if i.isdigit()]
        if len(product_item_info) != 3:
            raise FormInvalid(field='topic')
        # item_id/xx/object_id/ or item_id/xx/object_id/xxx
        object_id, item_id = product_item_info[0], product_item_info[2]
        lwm2m_item = Lwm2mItem.query \
            .filter(Lwm2mItem.objectID == object_id, Lwm2mItem.itemID == item_id) \
            .with_entities(Lwm2mItem.objectItem, Lwm2mItem.itemType).first()
        if not lwm2m_item:
            raise FormInvalid(field='topic')
        handled_payload['type'] = lwm2m_item.itemType
    return handled_payload
