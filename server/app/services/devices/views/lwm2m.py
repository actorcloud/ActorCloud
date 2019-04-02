from flask import jsonify, request, current_app, g
from sqlalchemy import func, distinct
from sqlalchemy.exc import IntegrityError

from actor_libs.database.orm import db
from actor_libs.decorators import ip_limit
from actor_libs.errors import (
    APIException, DataNotFound, ReferencedError, DataExisted, ParameterInvalid
)
from actor_libs.http_tools import SyncHttp
from actor_libs.http_tools.responses import handle_emqx_publish_response
from actor_libs.tasks.task import get_task_result
from actor_libs.utils import generate_uuid, get_delete_ids
from app import auth
from app.models import (
    Device, Product, Lwm2mObject, Lwm2mItem, Lwm2mInstanceItem, ProductItem, Lwm2mSubLog,
    DeviceControlLog
)
from . import bp
from ..schemas import (
    Lwm2mOperateSchema, Lwm2mObjectOperateSchema, ProductItemSchema, SearchLwm2mItemSchema
)


@bp.route('/devices/<int:device_id>/lwm2m_objects')
@auth.login_required
def list_device_objects(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = db.session \
        .query(Lwm2mObject, Lwm2mInstanceItem.objectAutoSub,
               func.count(distinct(Lwm2mInstanceItem.instanceID)).label('instanceCount'),
               func.count(distinct(Lwm2mInstanceItem.id)).label('itemCount')) \
        .join(Lwm2mInstanceItem,
              Lwm2mInstanceItem.objectID == Lwm2mObject.objectID) \
        .filter(Lwm2mInstanceItem.deviceIntID == device.id) \
        .group_by(Lwm2mObject, Lwm2mInstanceItem.objectAutoSub)
    records = query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/lwm2m_items')
@auth.login_required
def list_device_items(device_id):
    object_id = request.args.get('objectID')
    try:
        object_id = int(object_id)
    except Exception:
        raise ParameterInvalid(field='objectID')

    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = Lwm2mItem.query \
        .join(Lwm2mInstanceItem, Lwm2mInstanceItem.itemIntID == Lwm2mItem.id) \
        .with_entities(Lwm2mItem, Lwm2mInstanceItem.instanceID,
                       Lwm2mInstanceItem.itemAutoSub, Lwm2mInstanceItem.path,
                       Lwm2mInstanceItem.id.label('instanceItemIntID')) \
        .filter(Lwm2mItem.objectID == object_id,
                Lwm2mInstanceItem.deviceIntID == device.id) \
        .order_by(Lwm2mItem.itemID)

    records = query.pagination()
    return jsonify(records)


@bp.route('/devices/<int:device_id>/lwm2m_control_logs')
@auth.login_required
def list_device_lwm2m_control_logs(device_id):
    device = Device.query \
        .with_entities(Device.id) \
        .filter(Device.id == device_id) \
        .first_or_404()

    query = DeviceControlLog.query \
        .join(Lwm2mInstanceItem,
              Lwm2mInstanceItem.path == DeviceControlLog.path) \
        .join(Lwm2mItem, Lwm2mItem.id == Lwm2mInstanceItem.itemIntID) \
        .filter(Lwm2mInstanceItem.deviceIntID == device.id) \
        .with_entities(DeviceControlLog, Lwm2mInstanceItem.objectID,
                       Lwm2mInstanceItem.instanceID, Lwm2mItem.itemID,
                       Lwm2mItem.itemName, Lwm2mItem.itemType,
                       Lwm2mItem.itemUnit)
    records = query.pagination(code_list=['publishStatus'])
    return jsonify(records)


@bp.route('/products/<int:product_id>/lwm2m_items')
@auth.login_required
def list_product_items(product_id):
    query = Lwm2mItem.query \
        .outerjoin(ProductItem, ProductItem.itemIntID == Lwm2mItem.id) \
        .outerjoin(Product, Product.productID == ProductItem.productID) \
        .filter(Product.id == product_id,
                ProductItem.tenantID == g.tenant_uid) \
        .with_entities(Lwm2mItem.objectID, Lwm2mItem.itemID,
                       Lwm2mItem.itemName, Lwm2mItem.itemType,
                       Lwm2mItem.itemUnit, Lwm2mItem.itemOperations,
                       ProductItem.id)
    records = query.pagination()
    return jsonify(records)


@bp.route('/products/<int:product_id>/lwm2m_items', methods=['POST'])
@auth.login_required
def create_product_item(product_id):
    product = Product.query \
        .filter(Product.id == product_id,
                Product.cloudProtocol == 3) \
        .first_or_404()
    request_dict = ProductItemSchema.validate_request()
    lwm2m_item = Lwm2mItem.query \
        .filter(Lwm2mItem.objectID == request_dict.get('objectID'),
                Lwm2mItem.itemID == request_dict.get('itemID')) \
        .first()
    if not lwm2m_item:
        raise DataNotFound(field='lwm2m_items')
    query_product_item = ProductItem.query \
        .filter(ProductItem.objectID == request_dict.get('objectID'),
                ProductItem.itemID == request_dict.get('itemID'),
                ProductItem.productID == product.productID,
                ProductItem.tenantID == g.tenant_uid) \
        .first()
    if query_product_item:
        raise DataExisted(field='productItem')
    request_dict['itemIntID'] = lwm2m_item.id
    request_dict['productID'] = product.productID
    request_dict['userIntID'] = g.user_id
    request_dict['tenantID'] = g.tenant_uid
    product_item = ProductItem()
    product_item.create(request_dict)
    return '', 201


@bp.route('/products/<int:product_id>/lwm2m_items', methods=['DELETE'])
@auth.login_required
def delete_product_item(product_id):
    product = Product.query.filter(Product.id == product_id).first_or_404()
    try:
        ids = get_delete_ids()
        product_items = ProductItem.query \
            .filter(ProductItem.id.in_(ids)) \
            .filter(ProductItem.productID == product.productID,
                    ProductItem.tenantID == g.tenant_uid) \
            .all()
        for item in product_items:
            db.session.delete(item)
        db.session.commit()
    except IntegrityError:
        raise ReferencedError()
    return '', 204


@bp.route('/lwm2m_items')
@auth.login_required(permission_required=False)
def search_lwm2m_item():
    query_args = SearchLwm2mItemSchema.validate_args()
    object_id = query_args.get('objectID')
    item_id = query_args.get('itemID')
    lwm2m_item = Lwm2mItem.query \
        .filter(Lwm2mItem.objectID == object_id,
                Lwm2mItem.itemID == item_id) \
        .first_or_404()
    record = lwm2m_item.to_dict(only=['itemName', 'itemType', 'itemID', 'objectID'])
    return jsonify(record)


@bp.route('/lwm2m/objects/auto_sub', methods=['POST'])
@auth.login_required(permission_required=False)
def object_auto_sub():
    """
    {
        "tenantID": "",
        "productID": "",
        "deviceID": "",
        "callback": "http://ip:port/api/xxx"
        "payload": {"path":"/3","msgType":"observe/cancel_observe","taskID":12
    }
    """
    request_dict = Lwm2mObjectOperateSchema.validate_request()
    object_id = request_dict.get('objectID')
    device_id = request_dict.get('deviceIntID')
    instance_item = Lwm2mInstanceItem.query \
        .filter(Lwm2mInstanceItem.tenantID == g.tenant_uid,
                Lwm2mInstanceItem.deviceIntID == device_id,
                Lwm2mInstanceItem.objectID == object_id) \
        .with_entities(Lwm2mInstanceItem) \
        .first_or_404()

    path = '/' + str(object_id)
    msg_type = request_dict.get('msgType')
    payload = dict(msgType=msg_type, path=path)
    publish_type = 'objectAutoSub'
    lwm2m_sub_log = Lwm2mSubLog(
        deviceIntID=device_id,
        tenantID=g.tenant_uid,
        payload=payload,
        objectID=instance_item.objectID,
        taskID=generate_uuid(),
        publishType=publish_type,
        userIntID=g.user_id)
    db.session.add(lwm2m_sub_log)
    db.session.commit()

    payload["taskID"] = lwm2m_sub_log.taskID
    device = Device.query.filter(Device.id == device_id).first_or_404()
    data = get_request_payload(device, instance_item, payload)
    handled_response = lwm2m_sub(data)
    # 2 waiting 3 success 4 fail
    if handled_response.get('status') == 3:
        sub_result = get_task_result(
            status=3, message='Objects auto sub success')
        lwm2m_sub_log.publishStatus = 2
        update_sub_status(lwm2m_sub_log)
    else:
        sub_result = get_task_result(
            status=4, message=handled_response.get('error'))
    return jsonify(sub_result), 201


@bp.route('/lwm2m/items/auto_sub', methods=['POST'])
@auth.login_required(permission_required=False)
def item_auto_sub():
    """
    {
        ...,
        "payload": {"path":"/3/0/1","msgType":"observe/cancel_observe","taskID":12}
    }
    """
    request_dict = Lwm2mOperateSchema.validate_request()
    path, _, instance_item = item_pre_process(
        request_dict.get('instanceItemIntID'))

    msg_type = request_dict.get('msgType')
    payload = dict(msgType=msg_type, path=path)
    publish_type = 'itemAutoSub'
    lwm2m_sub_log = Lwm2mSubLog(
        deviceIntID=instance_item.deviceIntID,
        tenantID=g.tenant_uid,
        payload=payload,
        objectID=instance_item.objectID,
        instanceItemIntID=instance_item.id,
        publishType=publish_type,
        userIntID=g.user_id,
        taskID=generate_uuid())
    db.session.add(lwm2m_sub_log)
    db.session.commit()

    payload['taskID'] = lwm2m_sub_log.taskID
    device = Device.query \
        .filter(Device.id == instance_item.deviceIntID).first_or_404()
    data = get_request_payload(device, instance_item, payload)
    handled_response = lwm2m_sub(data)

    if handled_response.get('status') == 3:
        sub_result = get_task_result(
            status=3, message='Items auto sub success')
        lwm2m_sub_log.publishStatus = 2
        update_sub_status(lwm2m_sub_log)
    else:
        sub_result = get_task_result(
            status=4, message=handled_response.get('error'))
    return jsonify(sub_result), 201


@bp.route('/lwm2m/subscribe_callback', methods=['POST'])
@ip_limit
def lwm2m_sub_callback():
    """ lwm2m sub/unsub callback
    {
        "taskID": 123,
        "status": 1,
        "message": "",
        "tenantID": "",
        "productID": "",
        "deviceID": ""
    }
     """
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    task_id = request_dict.get('taskID')
    if task_id:
        lwm2m_control = Lwm2mSubLog.query \
            .filter(Lwm2mSubLog.taskID == task_id) \
            .first_or_404()
        lwm2m_control.publishStatus = request_dict.get('status')
        update_sub_status(lwm2m_control)
        db.session.commit()
    return ''


@bp.route('/lwm2m/instance_items', methods=['POST'])
@ip_limit
def update_lwm2m_instance_items():
    """
    LWM2M DISCOVER
    Called by EMQX
    {
        "tenantID": "",
        "productID": "",
        "deviceID": "",
        "items": [
            {"path":"/3/0/0"},
            {"path":"/3/0/1","pmin":1,"pmax":5,"lt",5}
        ],
        'instance':'/6/0'
    }
    items：Parse path only,temporarily not parsing other fields
    When object cannot be discovered,instance has a value
    """
    request_dict = request.get_json()
    if not request_dict:
        raise APIException()
    device_uid = request_dict.get('deviceID')
    tenant_uid = request_dict.get('tenantID')
    product_uid = request_dict.get('productID')
    items = request_dict.get('items')
    instance = request_dict.get('instance')

    device = Device.query \
        .filter(Device.tenantID == tenant_uid, Device.productID == product_uid,
                Device.deviceID == device_uid).first_or_404()

    # When object cannot be discovered,update all items of the object
    if instance:
        path_seg = instance[1:].split('/')
        if len(path_seg) == 2:
            object_id, instance_id = path_seg
            lwm2m_items = Lwm2mItem.query \
                .filter(Lwm2mItem.objectID == object_id) \
                .all()
            for lwm2m_item in lwm2m_items:
                path = instance + '/' + str(lwm2m_item.itemID)
                update_instance_item(device, lwm2m_item, instance_id,
                                     object_id, path)
    elif isinstance(items, list):
        for item in items:
            path = item.get('path')
            path_seg = path[1:].split('/')
            if len(path_seg) != 3:
                continue
            object_id, instance_id, item_id = path_seg
            lwm2m_item = Lwm2mItem.query \
                .filter(Lwm2mItem.objectID == object_id,
                        Lwm2mItem.itemID == item_id) \
                .first()
            if not lwm2m_item:
                continue
            update_instance_item(device, lwm2m_item, instance_id, object_id,
                                 path)

    return ''


def update_instance_item(device, lwm2m_item, instance_id, object_id, path):
    """
    Update Lwm2mInstanceItem and ProductItem
    """
    product_uid = device.productID
    tenant_uid = device.tenantID
    lwm2m_instance_item = Lwm2mInstanceItem.query \
        .filter(Lwm2mInstanceItem.deviceIntID == device.id,
                Lwm2mInstanceItem.productID == product_uid,
                Lwm2mInstanceItem.tenantID == tenant_uid,
                Lwm2mInstanceItem.path == path) \
        .first()
    if not lwm2m_instance_item:
        lwm2m_instance_item = Lwm2mInstanceItem(
            instanceID=instance_id,
            objectAutoSub=device.autoSub,
            itemAutoSub=device.autoSub,
            path=path,
            deviceIntID=device.id,
            objectID=object_id,
            itemIntID=lwm2m_item.id,
            productID=product_uid,
            tenantID=tenant_uid)
        db.session.add(lwm2m_instance_item)
    product_item = ProductItem.query \
        .filter(ProductItem.productID == product_uid,
                ProductItem.tenantID == tenant_uid,
                ProductItem.objectID == object_id,
                ProductItem.itemID == lwm2m_item.itemID) \
        .first()
    if not product_item:
        product_item = ProductItem(
            objectID=object_id,
            itemID=lwm2m_item.itemID,
            tenantID=tenant_uid,
            productID=product_uid,
            itemIntID=lwm2m_item.id)
        db.session.add(product_item)
    db.session.commit()


def get_request_payload(device, instance_item, payload):
    return {
        'tenantID': instance_item.tenantID,
        'productID': instance_item.productID,
        'deviceID': device.deviceID,
        'payload': payload,
        'callback': current_app.config.get('LWM2M_SUB_CALLBACK_URL')
    }


def item_pre_process(instance_item_int_id):
    instance_item, lwm2m_item = Lwm2mInstanceItem.query \
        .outerjoin(Lwm2mItem, Lwm2mItem.id == Lwm2mInstanceItem.itemIntID) \
        .filter(Lwm2mInstanceItem.tenantID == g.tenant_uid,
                Lwm2mInstanceItem.id == instance_item_int_id) \
        .with_entities(Lwm2mInstanceItem, Lwm2mItem) \
        .first_or_404()
    object_id, instance_id, item_id = \
        instance_item.objectID, instance_item.instanceID, lwm2m_item.itemID
    path = '/'.join(['', str(object_id), str(instance_id), str(item_id)])
    return path, lwm2m_item, instance_item


def update_sub_status(lwm2m_sub_log):
    msg_type = lwm2m_sub_log.payload.get('msgType')
    publish_status = lwm2m_sub_log.publishStatus
    value = get_sub_status(msg_type, publish_status)
    if lwm2m_sub_log.publishType == 'objectAutoSub':
        object_id = lwm2m_sub_log.objectID
        object_instances = Lwm2mInstanceItem.query \
            .filter(Lwm2mInstanceItem.objectID == object_id,
                    Lwm2mInstanceItem.deviceIntID == lwm2m_sub_log.deviceIntID,
                    Lwm2mInstanceItem.tenantID == lwm2m_sub_log.tenantID) \
            .all()
        for instance in object_instances:
            instance.objectAutoSub = value
            instance.itemAutoSub = value

    if lwm2m_sub_log.publishType == 'itemAutoSub':
        instance_item = Lwm2mInstanceItem.query \
            .filter(Lwm2mInstanceItem.tenantID == lwm2m_sub_log.tenantID,
                    Lwm2mInstanceItem.deviceIntID == lwm2m_sub_log.deviceIntID,
                    Lwm2mInstanceItem.id == lwm2m_sub_log.instanceItemIntID) \
            .first_or_404()
        instance_item.itemAutoSub = value
    db.session.commit()


def get_sub_status(msg_type, publish_status):
    """
    Return status by msg type
    :param msg_type: observe/cancel_observe
    :param publish_status: 1,2,3,4,5
    :return: 0：cancel observe
            1：observe
            2：observing
            3：canceling
    """
    if publish_status in [1, 2, 3]:
        value = 2 if msg_type == 'observe' else 3
    elif publish_status == 4:
        value = 1 if msg_type == 'observe' else 0
    elif publish_status == 5:
        value = 0 if msg_type == 'observe' else 1
    else:
        value = 0
    return value


VALUE_TYPE = {
    'Float': 'floatValue',
    'Time': 'timeValue',
    'Boolean': 'boolValue',
    'String': 'stringValue',
    'Integer': 'intValue'
}


def lwm2m_sub(request_payload):
    """ EMQX lwm2m sub """

    url = current_app.config.get('LWM2M_PUBLISH_URL')
    with SyncHttp(auth=current_app.config.get('EMQ_AUTH')) as sync_http:
        response = sync_http.post(url, json=request_payload)

    handled_response = handle_emqx_publish_response(response)
    return handled_response
