from base64 import b64encode
from typing import AnyStr, Tuple, Dict

from actor_libs.database.orm import db
from actor_libs.errors import DataNotFound
from app.models import Lwm2mItem, Lwm2mInstanceItem


__all__ = [
    'get_lwm2m_item_by_path', 'check_control_type', 'handle_control_payload'
]


def get_lwm2m_item_by_path(path: AnyStr, device_id: int, tenant_uid: AnyStr):
    query = db.session \
        .query(Lwm2mItem.itemOperations, Lwm2mItem.itemType) \
        .join(Lwm2mInstanceItem, Lwm2mInstanceItem.itemIntID == Lwm2mItem.id) \
        .filter(Lwm2mInstanceItem.path == path,
                Lwm2mInstanceItem.tenantID == tenant_uid,
                Lwm2mInstanceItem.deviceIntID == device_id) \
        .first()
    if not query:
        raise DataNotFound(field='path')
    item_operations, item_type = query.itemOperations, query.itemType
    return {'item_operations': item_operations, 'item_type': item_type}


def check_control_type(control_type: int, item_operations: AnyStr) -> bool:
    if any([
        control_type == 2 and 'R' not in item_operations,
        control_type == 3 and 'W' not in item_operations,
        control_type == 4 and 'E' not in item_operations
    ]):
        check_status = False
    else:
        check_status = True
    return check_status


def handle_control_payload(control_type: int, path: AnyStr, payload: AnyStr,
                           item_type: AnyStr) -> Tuple[Dict, Dict]:
    """
    Build LWM2M publish payload,value or args must be encrypted when publish
    origin payload used to store and encrypt payload used to publish
    """

    if control_type == 2:
        origin_payload = {
            'msgType': 'read',
            'path': path
        }
        encrypt_payload = origin_payload
    elif control_type == 3:
        origin_payload = {
            'msgType': 'write',
            'path': path,
            'value': payload,
            'valueType': item_type
        }
        encrypt_payload = {
            **origin_payload,
            'value': str(b64encode(payload.encode()), encoding='utf-8')
        }
    elif control_type == 4:
        origin_payload = {
            'msgType': 'execute',
            'path': path,
            'args': payload
        }
        encrypt_payload = {
            **origin_payload,
            'args': str(b64encode(payload.encode()), encoding='utf-8')
        }
    else:
        origin_payload, encrypt_payload = {}, {}
    return origin_payload, encrypt_payload
